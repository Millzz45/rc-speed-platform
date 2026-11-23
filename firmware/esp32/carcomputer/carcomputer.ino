/* D51 car computer, ESP32-S3 wrapper (Arduino-ESP32 core 3.x). Board: Waveshare ESP32-S3-Zero.
 *
 * STATUS: NOT compiled and NOT run on hardware yet (no ESP32 toolchain on the Mac, no board in hand). The control logic it
 * calls, cc_core.c, IS compiled and tested on the Mac (rnd/tests/test_tech.py). Copy cc_core.c / cc_core.h from ../../core
 * into this folder before building, and regenerate cc_config_car.h with rnd/tech/gen_config.py.
 *
 * Wiring (3.3 V logic; the ESP32-S3 is NOT 5 V tolerant: check the receiver's pulse height first, tech_parts_d51.md Q1):
 *   receiver CH2 (throttle) -> PIN_THR_IN      PIN_ESC_OUT -> ESC signal wire        (throttle passes THROUGH the computer)
 *   receiver CH1 (steering) -> servo directly, and tapped to PIN_STR_IN for the log  (steering does NOT pass through it)
 *   GPS (GEPRC GEP-M10) TX -> PIN_GPS_RX, RX <- PIN_GPS_TX
 *   gyro (LSM6DSOX) on I2C; rpm sensor signal -> PIN_RPM
 *   current sensor (Pololu ACS37220 150 A carrier, item 5291): in the ESC's battery + lead; VCC from this board's 3V3 pin (it takes
 *     3.15-3.45 V only, NOT the 5.8 V rail), GND, OUT -> PIN_CURR
 *   pack voltage: 10k from battery + to PIN_VBAT, 2.2k from PIN_VBAT to ground (12.6 V reads 2.27 V)
 *   thermistors: each 10k probe from 3V3 to its pin, 10k from the pin to ground
 * If this board stops, the ESC gets no pulses and falls back on its own signal-loss protection (R12 / R35).
 */
#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WebServer.h>
#include <LittleFS.h>
#include <esp_task_wdt.h>
extern "C" {
#include "cc_core.h"
}
#include "cc_config_car.h"

// ---- pins (ESP32-S3-Zero: GPIO33-37 are not available, GPIO21 is the on-board LED) ----
const int PIN_CURR = 1, PIN_VBAT = 2, PIN_NTC_MOTOR = 3, PIN_THR_IN = 4, PIN_STR_IN = 5, PIN_ESC_OUT = 6, PIN_NTC_ESC = 7;
const int PIN_GPS_RX = 8, PIN_GPS_TX = 9, PIN_SDA = 10, PIN_SCL = 11, PIN_RPM = 12;
const float CURR_A_PER_V = 1.0f / 0.0088f;  // Pololu ACS37220 150 A carrier: 8.8 mV/A about a 1.65 V zero (150 A reads 2.97 V); zero trimmed at start-up
const float CURR_SIGN = 1.0f;               // the sensor reads both directions: if the log shows negative amps under throttle, set -1
const float VBAT_GAIN = (10000.0f + 2200.0f) / 2200.0f;   // two-resistor divider, 10k over 2.2k, 1% parts
const uint8_t IMU_ADDR = 0x6A;              // LSM6DSOX default address [check against the ST data sheet]

// ---- pulse capture ----
volatile uint32_t thr_rise = 0, str_rise = 0, thr_us = 1500, str_us = 1500, thr_ms = 0;
volatile uint32_t rpm_last_us = 0, rpm_period_us = 0, rpm_ms = 0;
void IRAM_ATTR isrThr() { uint32_t t = micros(); if (digitalRead(PIN_THR_IN)) thr_rise = t; else { thr_us = t - thr_rise; thr_ms = millis(); } }
void IRAM_ATTR isrStr() { uint32_t t = micros(); if (digitalRead(PIN_STR_IN)) str_rise = t; else str_us = t - str_rise; }
void IRAM_ATTR isrRpm() { uint32_t t = micros(); uint32_t p = t - rpm_last_us; rpm_last_us = t; if (p > 150) { rpm_period_us = p; rpm_ms = millis(); } }

// ---- state ----
cc_state st; cc_ubx ubx; cc_peak peak;
float curr_zero_v = 0, yaw_bias = 0, gps_mps = 0, yaw_rps = 0;
uint32_t gps_ms = 0, imu_ms = 0;
WebServer server(80);
File logFile;
struct __attribute__((packed)) LogRec {     // 40 bytes, 50 Hz -> 2 kB/s: about 50 min in 6 MB of flash
    uint32_t t_ms; uint16_t thr_in, thr_out, str_in; uint16_t rpm_div4; int16_t amps_x10; uint16_t vbat_mv;
    uint16_t gps_cm_s, gps_sacc_cm_s; uint16_t head_x100; uint8_t fix, sv; int32_t lat_e7, lon_e7; int16_t yaw_mrad_s; uint16_t flags; uint8_t t_motor, t_esc;
};

static void gpsSend(const uint8_t *f, size_t n) { Serial1.write(f, n); Serial1.flush(); }
static void gpsSetup() {
    // frames from the u-blox M10 interface description (rnd/market/tech_parts_d51.md section 9): RAM layer, sent at every start
    static const uint8_t A[] = {0xB5,0x62,0x06,0x8A,0x1F,0x00,0x00,0x01,0x00,0x00,0x01,0x00,0x21,0x30,0x64,0x00,0x02,0x00,0x21,0x30,0x01,0x00,0x07,0x00,0x91,0x20,0x01,0x02,0x00,0x74,0x10,0x00,0x21,0x00,0x11,0x20,0x04,0x4F,0xB2};
    static const uint8_t B[] = {0xB5,0x62,0x06,0x8A,0x0E,0x00,0x00,0x01,0x00,0x00,0x22,0x00,0x31,0x10,0x00,0x25,0x00,0x31,0x10,0x00,0x68,0x3B};
    Serial1.begin(115200, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);       // the GEPRC listing says 115200; a module at 38400 needs frame C first
    delay(200); gpsSend(B, sizeof B); delay(600); gpsSend(A, sizeof A);   // constellation change resets the receiver: wait 0.5 s
}

static bool imuWrite(uint8_t reg, uint8_t v) { Wire.beginTransmission(IMU_ADDR); Wire.write(reg); Wire.write(v); return Wire.endTransmission() == 0; }
static bool imuReadZ(float *rps) {
    Wire.beginTransmission(IMU_ADDR); Wire.write(0x26); if (Wire.endTransmission(false) != 0) return false;   // OUTZ_L_G [check]
    if (Wire.requestFrom((int)IMU_ADDR, 2) != 2) return false;
    int16_t raw = (int16_t)(Wire.read() | (Wire.read() << 8));
    *rps = raw * 0.0175f * 0.0174533f;                                // 17.5 mdps/LSB at +-500 dps [check]
    return true;
}

static float ntcC(int pin) {                                          // 10k B3950 to 3.3 V, 10k to ground
    float v = analogReadMilliVolts(pin) / 1000.0f; if (v < 0.05f || v > 3.25f) return 0;
    float r = 10000.0f * (3.3f - v) / v;
    return 1.0f / (1.0f / 298.15f + logf(r / 10000.0f) / 3950.0f) - 273.15f;
}

static void handleLog() {
    File f = LittleFS.open("/run.bin", "r"); if (!f) { server.send(404, "text/plain", "no log"); return; }
    server.setContentLength(CONTENT_LENGTH_UNKNOWN);
    server.send(200, "text/csv", "t_ms,thr_in_us,thr_out_us,str_in_us,str_out_us,motor_rpm,amps,vbat,gps_mps,gps_sacc_mps,gps_head_deg,gps_fix,gps_sv,lat_e7,lon_e7,yaw_rps,flags\n");
    LogRec r; char line[200];
    while (f.read((uint8_t *)&r, sizeof r) == sizeof r) {
        snprintf(line, sizeof line, "%lu,%u,%u,%u,%u,%u,%.1f,%.2f,%.2f,%.2f,%.2f,%u,%u,%ld,%ld,%.3f,%u\n", (unsigned long)r.t_ms, r.thr_in, r.thr_out, r.str_in, r.str_in,
                 r.rpm_div4 * 4u, r.amps_x10 / 10.0, r.vbat_mv / 1000.0, r.gps_cm_s / 100.0, r.gps_sacc_cm_s / 100.0, r.head_x100 / 100.0, r.fix, r.sv, (long)r.lat_e7, (long)r.lon_e7, r.yaw_mrad_s / 1000.0, r.flags);
        server.sendContent(line);
        esp_task_wdt_reset();
    }
    f.close(); server.sendContent("");
}

void setup() {
    pinMode(PIN_THR_IN, INPUT_PULLDOWN); pinMode(PIN_STR_IN, INPUT_PULLDOWN); pinMode(PIN_RPM, INPUT_PULLUP);
    ledcAttach(PIN_ESC_OUT, 50, 14); ledcWrite(PIN_ESC_OUT, (uint32_t)(1500.0f / 20000.0f * 16383.0f));   // neutral before anything else
    attachInterrupt(PIN_THR_IN, isrThr, CHANGE); attachInterrupt(PIN_STR_IN, isrStr, CHANGE); attachInterrupt(PIN_RPM, isrRpm, FALLING);
    analogSetAttenuation(ADC_11db);
    Wire.begin(PIN_SDA, PIN_SCL, 400000);
    imuWrite(0x11, 0x64);                                             // CTRL2_G: 416 Hz, +-500 dps [check]
    gpsSetup();
    cc_init(&st); cc_ubx_init(&ubx); cc_peak_init(&peak, 10);         // best mean over 10 fixes = 1 s at 10 Hz
    delay(300);
    float z = 0, yb = 0; int n = 0;
    for (int i = 0; i < 100; i++) { z += analogReadMilliVolts(PIN_CURR) / 1000.0f; float y; if (imuReadZ(&y)) { yb += y; n++; } delay(5); }
    curr_zero_v = z / 100.0f; yaw_bias = n ? yb / n : 0;              // car at rest, motor off: zero the current sensor and the gyro
    LittleFS.begin(true); logFile = LittleFS.open("/run.bin", "w");
    WiFi.softAP("carcomputer");                                       // phone joins this network; http://192.168.4.1/log.csv
    server.on("/log.csv", handleLog);
    server.on("/", []() { char b[160]; snprintf(b, sizeof b, "best 1 s speed %.1f mph\nlast %.1f mph\n<a href=/log.csv>log</a>", peak.best * 2.23694f, gps_mps * 2.23694f); server.send(200, "text/html", b); });
    server.begin();
    esp_task_wdt_config_t w = {.timeout_ms = 500, .idle_core_mask = 0, .trigger_panic = true}; esp_task_wdt_reconfigure(&w); esp_task_wdt_add(NULL);
}

void loop() {
    static uint32_t next = 0, nlog = 0; static cc_out out;
    while (Serial1.available()) if (cc_ubx_byte(&ubx, (uint8_t)Serial1.read())) {
        if (ubx.fix_type >= 3 && (ubx.flags & 1)) { gps_mps = ubx.gspeed_mm_s / 1000.0f; gps_ms = millis(); cc_peak_add(&peak, gps_mps); }
    }
    uint32_t now = millis();
    if ((int32_t)(now - next) >= 0) {                                 // 100 Hz control tick
        next = now + 10;
        float y; if (imuReadZ(&y)) { yaw_rps = y - yaw_bias; imu_ms = now; }
        noInterrupts(); uint32_t tu = thr_us, su = str_us, tms = thr_ms, rp = rpm_period_us, rms = rpm_ms; interrupts();
        cc_in in = {};
        in.now_ms = now; in.thr_in_us = tu; in.str_in_us = su; in.t_rx_ms = tms;
        bool turning = rp > 0 && (now - rms) < 60;                    // no edge for 60 ms = stopped (1000 rpm gives one every 30 ms)
        in.motor_rpm = turning ? 60.0e6f / ((float)rp * CC_POLE_PAIRS) : 0.0f; in.t_rpm_ms = now;
        in.amps = CURR_SIGN * (analogReadMilliVolts(PIN_CURR) / 1000.0f - curr_zero_v) * CURR_A_PER_V; in.vbat = analogReadMilliVolts(PIN_VBAT) / 1000.0f * VBAT_GAIN; in.t_amp_ms = now;
        in.gps_mps = gps_mps; in.t_gps_ms = gps_ms; in.yaw_rps = yaw_rps; in.t_imu_ms = imu_ms;
        cc_step(&CC_CAR, &st, &in, &out);
        ledcWrite(PIN_ESC_OUT, (uint32_t)(out.thr_out_us / 20000.0f * 16383.0f));
        if (logFile && (++nlog & 1) == 0) {                              // 50 Hz log
            LogRec r = {}; r.t_ms = now; r.thr_in = tu; r.thr_out = (uint16_t)out.thr_out_us; r.str_in = su; r.rpm_div4 = (uint16_t)(in.motor_rpm / 4);
            r.amps_x10 = (int16_t)(in.amps * 10); r.vbat_mv = (uint16_t)(in.vbat * 1000); r.gps_cm_s = (uint16_t)(gps_mps * 100); r.gps_sacc_cm_s = (uint16_t)(ubx.sacc_mm_s / 10);
            r.head_x100 = (uint16_t)(ubx.head_e5 / 1000); r.fix = ubx.fix_type; r.sv = ubx.num_sv; r.lat_e7 = ubx.lat_e7; r.lon_e7 = ubx.lon_e7;
            r.yaw_mrad_s = (int16_t)(yaw_rps * 1000); r.flags = (uint16_t)out.flags; r.t_motor = (uint8_t)ntcC(PIN_NTC_MOTOR); r.t_esc = (uint8_t)ntcC(PIN_NTC_ESC);
            logFile.write((const uint8_t *)&r, sizeof r);
            if ((nlog & 0xFF) == 0) logFile.flush();
        }
        esp_task_wdt_reset();
    }
    if (fabsf(out.u_in) < 0.01f && gps_mps < 0.5f) server.handleClient();   // serve the phone only when parked
}
