import streamlit as st
import numpy as np
import plotly.graph_objects as go
import math

SECONDS_PER_YEAR = 365 * 24 * 3600
TARGET_UTILIZATION = 0.9
CURVE_STEEPNESS = 4.0
ADJUSTMENT_SPEED_PER_SECOND = 50.0 / SECONDS_PER_YEAR
INITIAL_RATE_AT_TARGET_APR = 0.04
MIN_RATE_AT_TARGET_APR = 0.01
MAX_RATE_AT_TARGET_APR = 1000.0

def curve(rate_at_target, err, c):
    coeff = (1 - 1 / c) if err < 0 else (c - 1)
    return (coeff * err + 1) * rate_at_target

def infer_rate_at_target(borrow_rate, err, c):
    coeff = (1 - 1 / c) if err < 0 else (c - 1)
    denom = coeff * err + 1
    denom = denom if denom != 0 else 1e-12
    return borrow_rate / denom

def normalized_err(u, target):
    err_norm = (1 - target) if u > target else target
    if err_norm == 0:
        return 0.0
    return (u - target) / err_norm

def new_rate_at_target(start_rate_at_target, linear_adaptation, min_r, max_r):
    val = start_rate_at_target * math.exp(linear_adaptation)
    return max(min(val, max_r), min_r)

def simulate(u_pct, b_pct, hours):
    u = u_pct / 100.0
    target = TARGET_UTILIZATION
    err = normalized_err(u, target)
    start_rt = infer_rate_at_target(b_pct / 100.0, err, CURVE_STEEPNESS)
    la = (ADJUSTMENT_SPEED_PER_SECOND * err) * (hours * 3600.0)
    end_rt = new_rate_at_target(start_rt, la, MIN_RATE_AT_TARGET_APR, MAX_RATE_AT_TARGET_APR)
    mid_rt = new_rate_at_target(start_rt, la / 2.0, MIN_RATE_AT_TARGET_APR, MAX_RATE_AT_TARGET_APR)
    avg_rt = (start_rt + end_rt + 2 * mid_rt) / 4.0
    end_borrow = curve(end_rt, err, CURVE_STEEPNESS) * 100.0
    avg_borrow = curve(avg_rt, err, CURVE_STEEPNESS) * 100.0
    return err, start_rt * 100.0, end_rt * 100.0, avg_rt * 100.0, end_borrow, avg_borrow

def render():
    st.title("Adaptive Curve IRM Simulator")
    st.markdown("Simulate future borrow rates from current utilization and borrow rate, annualized rates with time in hours.")

    with st.sidebar:
        u_pct = st.number_input("Current Utilization (%)", min_value=0.0, max_value=100.0, value=80.0, step=0.1, help="Assumed constant during the time horizon.")
        b_pct = st.number_input("Current Borrow Rate (APR, %)", min_value=0.0, max_value=1000.0, value=5.0, step=0.1, help="Annualized borrow rate at the current utilization.")
        use_days = st.toggle("Use days for time axis", value=False)
        if not use_days:
            h_max = st.number_input("Horizon (hours)", min_value=1, max_value=8760, value=240, step=1)
        else:
            h_max = st.number_input("Horizon (days)", min_value=1, max_value=3650, value=10, step=1)
        show_avg = st.toggle(
            "Show average rate over interval",
            value=True,
            help="Average rate is the trapezoidal approximation of the integral of the curve over the horizon; end rate is the instantaneous rate at the end of the horizon."
        )

    times = np.linspace(0, h_max, int(h_max) + 1)
    end_rates = []
    avg_rates = []
    for t in times:
        t_hours = float(t) if not use_days else float(t) * 24.0
        _, _, _, _, end_borrow, avg_borrow = simulate(u_pct, b_pct, t_hours)
        end_rates.append(end_borrow)
        avg_rates.append(avg_borrow)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=end_rates, mode="lines", name="End Borrow Rate (APR, %)", line=dict(width=3)))
    if show_avg:
        fig.add_trace(go.Scatter(x=times, y=avg_rates, mode="lines", name="Average Borrow Rate (APR, %)", line=dict(width=2, dash="dash")))
    fig.update_layout(
        title={"text": "<span style=\"font-weight:normal\">Borrow Rate vs Time</span>", "x": 0.48, "xanchor": "center"},
        title_font=dict(size=22),
        height=500,
        plot_bgcolor="#f0f0f0",
        paper_bgcolor="#f0f0f0",
        margin=dict(l=80, r=80, t=60, b=50)
    )
    fig.update_xaxes(title_text=("Days" if use_days else "Hours"), showgrid=True, gridcolor='rgba(128,128,128,0.3)', gridwidth=1)
    fig.update_yaxes(title_text="Rate (APR, %)")

    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown("**Model Constants (fixed):**")
        st.write({
            "Target Utilization (%)": TARGET_UTILIZATION * 100.0,
            "Curve Steepness (C)": CURVE_STEEPNESS,
            "Adjustment Speed (per second, per year=50)": ADJUSTMENT_SPEED_PER_SECOND,
            "Initial Rate At Target (APR, %)": INITIAL_RATE_AT_TARGET_APR * 100.0,
            "Min Rate At Target (APR, %)": MIN_RATE_AT_TARGET_APR * 100.0,
            "Max Rate At Target (APR, %)": MAX_RATE_AT_TARGET_APR * 100.0,
        })
        horizon_hours = float(h_max) if not use_days else float(h_max) * 24.0
        err_val, start_rt_pct, end_rt_pct, avg_rt_pct, end_borrow, avg_borrow = simulate(u_pct, b_pct, horizon_hours)
        st.subheader("Summary")
        st.write({
            "Normalized Error": round(err_val, 6),
            "Start Rate At Target (APR, %)": round(start_rt_pct, 6),
            "End Rate At Target @ horizon (APR, %)": round(end_rt_pct, 6),
            "Average Rate At Target over horizon (APR, %)": round(avg_rt_pct, 6),
            "End Borrow Rate @ horizon (APR, %)": round(end_borrow, 6),
            "Average Borrow Rate over horizon (APR, %)": round(avg_borrow, 6)
        })

    with col_right:
        st.plotly_chart(fig, use_container_width=True)

def main():
    render()

if __name__ == "__main__":
    main()