/* D51 car computer control core. See cc_core.h. */
#include "cc_core.h"
#include <math.h>
#include <string.h>

static float clampf(float x, float lo, float hi) { return x < lo ? lo : x > hi ? hi : x; }
static int fresh(uint32_t now, uint32_t t, uint32_t timeout) { return t != 0 && (uint32_t)(now - t) <= timeout; }

void cc_init(cc_state *s) { memset(s, 0, sizeof *s); }

float cc_cap_amps(const cc_config *c, float rpm)
{
    if (!(rpm > c->cap_rpm[0])) return c->cap_amp[0];            /* also catches NaN */
    for (int i = 1; i < CC_CAP_N; i++)
        if (rpm <= c->cap_rpm[i]) {
            float f = (rpm - c->cap_rpm[i - 1]) / (c->cap_rpm[i] - c->cap_rpm[i - 1]);
            return c->cap_amp[i - 1] + f * (c->cap_amp[i] - c->cap_amp[i - 1]);
        }
    return c->cap_amp[CC_CAP_N - 1];
}

static float cap_min(const cc_config *c)
{
    float m = c->cap_amp[0];
    for (int i = 1; i < CC_CAP_N; i++) if (c->cap_amp[i] < m) m = c->cap_amp[i];
    return m;
}

void cc_step(const cc_config *c, cc_state *s, const cc_in *in, cc_out *o)
{
    memset(o, 0, sizeof *o);
    float dt = s->started ? (float)(uint32_t)(in->now_ms - s->last_ms) * 1e-3f : 0.0f;
    dt = clampf(dt, 0.0f, 0.1f);
    s->last_ms = in->now_ms; s->started = 1;

    /* ---- receiver ---- */
    int rx_ok = fresh(in->now_ms, in->t_rx_ms, c->rx_timeout_ms)
                && in->thr_in_us >= 800.0f && in->thr_in_us <= 2200.0f
                && in->str_in_us >= 800.0f && in->str_in_us <= 2200.0f;
    if (!rx_ok) {                                  /* NaN pulses fail the comparisons above and land here too */
        o->thr_out_us = c->thr_neutral_us; o->str_out_us = c->str_neutral_us;
        o->flags = CC_F_RX_LOST; s->u_prev = 0.0f; s->capped = 0;
        return;
    }

    int rpm_ok = fresh(in->now_ms, in->t_rpm_ms, c->rpm_timeout_ms) && in->motor_rpm >= 0.0f && in->motor_rpm < 2.0e5f;
    int amp_ok = fresh(in->now_ms, in->t_amp_ms, c->amp_timeout_ms) && in->amps > -50.0f && in->amps < 1000.0f;
    int gps_ok = fresh(in->now_ms, in->t_gps_ms, c->gps_timeout_ms) && in->gps_mps >= 0.0f && in->gps_mps < 100.0f;
    /* an rpm reading far below what the road speed needs is a dead sensor, not a stopped motor */
    if (rpm_ok && gps_ok && in->gps_mps > 3.0f && in->motor_rpm * c->mps_per_motor_rpm < 0.5f * in->gps_mps) rpm_ok = 0;
    int imu_ok = fresh(in->now_ms, in->t_imu_ms, c->imu_timeout_ms) && fabsf(in->yaw_rps) < 40.0f;
    float vb = (in->vbat > 6.0f && in->vbat < 14.0f) ? in->vbat : c->v_assumed;   /* missing or silly -> the full-pack value: a lower ceiling */
    if (!rpm_ok) o->flags |= CC_F_NO_RPM;
    if (!amp_ok) o->flags |= CC_F_NO_AMP;

    /* no rpm pickup (or a dead one): take motor speed from GPS road speed. It reads low in wheelspin and lags a hard launch,
     * both of which make the ceiling stricter, never looser. gps_rpm_gain allows for the tyre slip of a driven wheel at speed. */
    float rpm = in->motor_rpm;
    if (!rpm_ok && gps_ok && c->gps_rpm_gain > 0.0f) {
        rpm = in->gps_mps / c->mps_per_motor_rpm * c->gps_rpm_gain; rpm_ok = 1;
        o->flags &= ~(uint32_t)CC_F_NO_RPM; o->flags |= CC_F_GPS_RPM;
    }
    int v_ok = 1; float v = 0.0f;
    if (gps_ok) v = in->gps_mps;
    else if (rpm_ok) v = rpm * c->mps_per_motor_rpm;     /* reads high in wheelspin: the cautious side for both users */
    else { v_ok = 0; o->flags |= CC_F_NO_SPEED; }
    o->speed_mps = v;

    /* ---- throttle ---- */
    float span = c->thr_full_us - c->thr_neutral_us;               /* signed: a reversed channel works too */
    float x = (in->thr_in_us - c->thr_neutral_us) / span;
    float dead = c->thr_dead_us / fabsf(span);
    if (!(x > dead)) {                                             /* neutral, brake, reverse: untouched */
        o->thr_out_us = in->thr_in_us;
        if (x < -dead) o->flags |= CC_F_BRAKE;
        s->u_prev = 0.0f; s->capped = 0;
    } else {
        float u = clampf((x - dead) / (1.0f - dead), 0.0f, 1.0f);
        float u_cap;
        if (rpm_ok) {
            float icap = cc_cap_amps(c, rpm);
            float u_ff = (icap * c->r_total_ohm + rpm / c->kv_rpm_per_v) / vb / c->esc_gain;
            if (amp_ok) {
                /* current error as throttle: the loop then has the same speed (trim_ki, 1/s) at every rpm. Down fast, up at a quarter
                 * of that, and only while the ceiling is what holds the car back */
                /* the sensor is in the battery lead: battery current = duty x motor current */
                float duty = clampf(s->u_prev * c->esc_gain, 0.08f, 1.0f);
                float e = (in->amps / duty - icap) * c->r_total_ohm / vb / c->esc_gain;
                if (e > 0.0f) s->trim += c->trim_ki * e * dt;
                else if (s->capped) s->trim += 0.25f * c->trim_ki * e * dt;
            } else if (!amp_ok) {
                s->trim += (s->trim > 0.0f ? -1.0f : 1.0f) * c->trim_decay * dt;   /* no reading: forget the correction slowly */
                if (fabsf(s->trim) < c->trim_decay * dt) s->trim = 0.0f;
            }
            s->trim = clampf(s->trim, -c->trim_max, c->trim_max);
            o->i_cap_a = icap;
            u_cap = u_ff - s->trim;
        } else {
            float icap = cap_min(c);
            o->i_cap_a = icap;
            float u0 = icap * c->r_total_ohm / vb / c->esc_gain;   /* the ceiling at standstill: a safe place to start the ramp */
            u_cap = (s->u_prev > u0 ? s->u_prev : u0) + c->thr_slew_per_s * dt;   /* then ramp, like an ESC punch setting */
            if (amp_ok) { if (in->amps / clampf(s->u_prev * c->esc_gain, 0.08f, 1.0f) > icap) u_cap = s->u_prev - 2.0f * c->thr_slew_per_s * dt; }
            else { o->flags |= CC_F_LIMP; if (u_cap > c->thr_limp) u_cap = c->thr_limp; }
        }
        if (c->v_limit_mps > 0.0f) {
            float rpm_lim = c->v_limit_mps / c->mps_per_motor_rpm, u_v;
            if (v_ok) u_v = ((rpm_lim / c->kv_rpm_per_v + c->i_cruise_a * c->r_total_ohm) / vb + c->v_kp * (c->v_limit_mps - v)) / c->esc_gain;
            else u_v = rpm_lim / c->kv_rpm_per_v / c->v_assumed / c->esc_gain;   /* cannot pass the limit even unloaded */
            if (u_v < u_cap) { u_cap = u_v; o->flags |= CC_F_SPEEDCAP; }
        }
        if (!(u_cap >= 0.0f)) u_cap = 0.0f;                          /* NaN or negative -> 0 */
        float uo = u < u_cap ? u : u_cap;
        if (uo < u) o->flags |= CC_F_CAPPED; else o->flags &= ~(uint32_t)CC_F_SPEEDCAP;
        o->u_in = u; o->u_out = uo; o->u_cap = u_cap;
        s->u_prev = uo; s->capped = uo < u;
        o->thr_out_us = c->thr_neutral_us + (dead + uo * (1.0f - dead)) * span;
    }

    /* ---- steering ---- */
    float sx = clampf((in->str_in_us - c->str_neutral_us) / c->str_span_us, -1.0f, 1.0f);
    float corr = 0.0f;
    if (c->yaw_gain > 0.0f && imu_ok && v_ok) {
        float q = v / c->yaw_v_ref_mps;
        float g = c->yaw_gain / (1.0f + q * q) * clampf(v / c->yaw_fade_mps, 0.0f, 1.0f);
        float r_ref = v * sx * c->str_lock_rad / (c->wheelbase_m * (1.0f + c->k_us * v * v));
        corr = -c->yaw_sign * g * (in->yaw_rps - r_ref) / c->str_lock_rad;
        if (fabsf(corr) >= c->yaw_max_frac) { corr = corr > 0 ? c->yaw_max_frac : -c->yaw_max_frac; o->flags |= CC_F_YAW_SAT; }
        if (corr != 0.0f) o->flags |= CC_F_YAW_ON;
    }
    o->yaw_corr_frac = corr;
    o->str_out_us = c->str_neutral_us + clampf(sx + corr, -1.0f, 1.0f) * c->str_span_us;
}

/* ------------------------------------------------------------------ best sustained speed */
void cc_peak_init(cc_peak *p, int win)
{
    memset(p, 0, sizeof *p);
    p->win = win < 1 ? 1 : win > CC_PEAK_N ? CC_PEAK_N : win;
}

float cc_peak_add(cc_peak *p, float mps)
{
    if (p->n == p->win) { p->sum -= p->buf[p->head]; } else p->n++;
    p->buf[p->head] = mps; p->sum += mps; p->head = (p->head + 1) % p->win;
    if (p->n == p->win) {
        float m = 0.0f;                               /* re-sum: no drift over a long run */
        for (int i = 0; i < p->win; i++) m += p->buf[i];
        p->sum = m; m /= (float)p->win;
        if (m > p->best) p->best = m;
    }
    return p->best;
}

/* ------------------------------------------------------------------ UBX NAV-PVT */
static int32_t i4(const uint8_t *p) { return (int32_t)((uint32_t)p[0] | (uint32_t)p[1] << 8 | (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24); }

void cc_ubx_init(cc_ubx *u) { memset(u, 0, sizeof *u); }

int cc_ubx_byte(cc_ubx *u, uint8_t b)
{
    switch (u->st) {
    case 0: u->st = (b == 0xB5); return 0;
    case 1: u->st = (b == 0x62) ? 2 : (b == 0xB5); return 0;
    case 2: u->cls = b; u->ck_a = b; u->ck_b = b; u->st = 3; return 0;
    case 3: u->id = b; u->ck_a += b; u->ck_b += u->ck_a; u->st = 4; return 0;
    case 4: u->len = b; u->ck_a += b; u->ck_b += u->ck_a; u->st = 5; return 0;
    case 5:
        u->len |= (uint16_t)b << 8; u->ck_a += b; u->ck_b += u->ck_a; u->idx = 0;
        u->st = u->len > sizeof u->pay ? 0 : u->len ? 6 : 7;      /* longer than anything we read: not ours, look for the next sync */
        return 0;
    case 6:
        if (u->idx < sizeof u->pay) u->pay[u->idx] = b;
        u->idx++; u->ck_a += b; u->ck_b += u->ck_a;
        if (u->idx >= u->len) u->st = 7;
        return 0;
    case 7: u->st = (b == u->ck_a) ? 8 : 0; return 0;
    default:
        u->st = 0;
        if (b != u->ck_b || u->cls != 0x01 || u->id != 0x07 || u->len != 92) return 0;
        u->itow_ms = (uint32_t)i4(u->pay + 0);
        u->fix_type = u->pay[20]; u->flags = u->pay[21]; u->num_sv = u->pay[23];
        u->lon_e7 = i4(u->pay + 24); u->lat_e7 = i4(u->pay + 28);
        u->hacc_mm = (uint32_t)i4(u->pay + 40);
        u->gspeed_mm_s = i4(u->pay + 60); u->head_e5 = i4(u->pay + 64);
        u->sacc_mm_s = (uint32_t)i4(u->pay + 68);
        return 1;
    }
}
