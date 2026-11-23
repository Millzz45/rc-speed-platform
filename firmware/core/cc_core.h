/* D51 car computer: control core. Plain C99, no hardware calls, so the same file runs on the ESP32 and inside the
 * Mac simulations (rnd/tech/sim, loaded through ctypes).
 *
 * What it does every control tick (cc_step):
 *   throttle   passes the driver's throttle through a ceiling. The ceiling is the ESC duty that gives the allowed motor
 *              current at the measured motor rpm (feed-forward, from the motor's kv and the circuit resistance), pulled
 *              down further if the current sensor reads over the limit. It can only LOWER forward throttle. Neutral,
 *              brake and reverse pass through untouched.
 *   speed cap  optional ceiling on true (GPS) road speed for first runs.
 *   steering   adds a yaw-rate correction: measured yaw rate minus the yaw rate the driver is asking for at this speed.
 *              The gain falls with speed. Off when speed is not known.
 *   faults     no receiver pulses -> neutral throttle, centred steering. A sensor that stops updating drops the function
 *              that needs it to a slower, safer fallback; it never raises throttle.
 */
#ifndef CC_CORE_H
#define CC_CORE_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

#define CC_CAP_N 4

enum {
    CC_F_RX_LOST   = 1 << 0,   /* no valid receiver pulses: outputs forced to neutral */
    CC_F_CAPPED    = 1 << 1,   /* the throttle ceiling is below the driver's demand */
    CC_F_NO_RPM    = 1 << 2,   /* rpm not valid: ramp fallback in use */
    CC_F_NO_AMP    = 1 << 3,   /* current not valid: no trim */
    CC_F_LIMP      = 1 << 4,   /* neither rpm nor current: fixed throttle ceiling */
    CC_F_SPEEDCAP  = 1 << 5,   /* the road-speed limiter is the active ceiling */
    CC_F_NO_SPEED  = 1 << 6,   /* no GPS and no rpm: yaw assist off */
    CC_F_YAW_ON    = 1 << 7,   /* yaw assist is adding steering */
    CC_F_YAW_SAT   = 1 << 8,   /* yaw correction is at its limit */
    CC_F_BRAKE     = 1 << 9,   /* driver is below neutral (brake light) */
    CC_F_GPS_RPM   = 1 << 10   /* motor speed is being taken from GPS road speed */
};

typedef struct {
    /* radio pulses, microseconds */
    float thr_neutral_us, thr_full_us, thr_dead_us;
    float str_neutral_us, str_span_us;
    float str_lock_rad;                /* road-wheel angle at full stick */
    /* motor circuit for the feed-forward ceiling */
    float kv_rpm_per_v, r_total_ohm;   /* resistance of motor + ESC + their leads (not the pack: its drop is in the measured voltage) */
    float esc_gain;                    /* ESC duty per unit forward throttle; 1 = linear. From the bench calibration */
    float v_assumed;                   /* pack voltage used when the reading is missing (use the full-pack value) */
    /* allowed motor current against motor rpm (flat outside the table) */
    float cap_rpm[CC_CAP_N], cap_amp[CC_CAP_N];
    float trim_ki, trim_decay, trim_max;   /* current trim on the ceiling: loop speed (1/s), forget rate and limit (throttle units) */
    float thr_slew_per_s;              /* fallback: forward throttle may rise this fast (1 = full scale per second) */
    float thr_limp;                    /* fallback ceiling 0..1 when neither rpm nor current is valid */
    /* road-speed limiter; v_limit_mps = 0 turns it off */
    float v_limit_mps, v_kp, i_cruise_a, mps_per_motor_rpm;
    float gps_rpm_gain;                /* > 0: use GPS speed x this as motor speed when there is no rpm reading (1.03 = 3% tyre slip allowed for) */
    /* yaw assist; yaw_gain = 0 turns it off. gain(v) = yaw_gain / (1 + (v / yaw_v_ref)^2), in rad of steer per rad/s */
    float yaw_gain, yaw_v_ref_mps, yaw_max_frac, yaw_sign, yaw_fade_mps;
    float wheelbase_m, k_us;           /* reference yaw rate = v * steer / (L * (1 + k_us * v^2)) */
    /* a reading older than this is not used */
    uint32_t rx_timeout_ms, rpm_timeout_ms, amp_timeout_ms, gps_timeout_ms, imu_timeout_ms;
} cc_config;

typedef struct {
    uint32_t now_ms;
    float thr_in_us, str_in_us; uint32_t t_rx_ms;
    float motor_rpm;            uint32_t t_rpm_ms;
    float amps, vbat;           uint32_t t_amp_ms;   /* BATTERY-lead current and the voltage at the ESC */
    float gps_mps;              uint32_t t_gps_ms;
    float yaw_rps;              uint32_t t_imu_ms;
} cc_in;

typedef struct {
    float thr_out_us, str_out_us;
    float u_in, u_out, u_cap;   /* forward throttle 0..1: asked, sent, ceiling */
    float i_cap_a, speed_mps, yaw_corr_frac;
    uint32_t flags;
} cc_out;

typedef struct {
    uint32_t last_ms; int started, capped;
    float u_prev, trim;
} cc_state;

void cc_init(cc_state *s);
void cc_step(const cc_config *c, cc_state *s, const cc_in *in, cc_out *out);
float cc_cap_amps(const cc_config *c, float motor_rpm);

/* ---- best sustained speed: highest mean GPS speed over a fixed window (default 1 s) ---- */
#define CC_PEAK_N 64
typedef struct { float buf[CC_PEAK_N]; int n, head, win; float sum, best; } cc_peak;
void cc_peak_init(cc_peak *p, int window_samples);
float cc_peak_add(cc_peak *p, float mps);

/* ---- u-blox UBX NAV-PVT reader (byte at a time). Returns 1 when a checked NAV-PVT frame has just completed ---- */
typedef struct {
    uint8_t st, cls, id, ck_a, ck_b; uint16_t len, idx; uint8_t pay[100];
    /* last decoded fix */
    uint32_t itow_ms; uint8_t fix_type, flags, num_sv;
    int32_t lon_e7, lat_e7, gspeed_mm_s, head_e5; uint32_t sacc_mm_s, hacc_mm;
} cc_ubx;
void cc_ubx_init(cc_ubx *u);
int cc_ubx_byte(cc_ubx *u, uint8_t b);

#ifdef __cplusplus
}
#endif
#endif
