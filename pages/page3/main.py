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

def normalized_err(u, target):
    err_norm = (1 - target) if u > target else target
    if err_norm == 0:
        return 0.0
    return (u - target) / err_norm

def new_rate_at_target(start_rate_at_target, linear_adaptation, min_r, max_r):
    val = start_rate_at_target * math.exp(linear_adaptation)
    return max(min(val, max_r), min_r)

def simulate(u_pct, start_kink_pct, hours):
    u = u_pct / 100.0
    target = TARGET_UTILIZATION
    err = normalized_err(u, target)
    
    # Input is now Kink Rate (Rate at Target)
    start_rt = start_kink_pct / 100.0
    
    la = (ADJUSTMENT_SPEED_PER_SECOND * err) * (hours * 3600.0)
    end_rt = new_rate_at_target(start_rt, la, MIN_RATE_AT_TARGET_APR, MAX_RATE_AT_TARGET_APR)
    mid_rt = new_rate_at_target(start_rt, la / 2.0, MIN_RATE_AT_TARGET_APR, MAX_RATE_AT_TARGET_APR)
    avg_rt = (start_rt + end_rt + 2 * mid_rt) / 4.0
    
    end_borrow = curve(end_rt, err, CURVE_STEEPNESS) * 100.0
    avg_borrow = curve(avg_rt, err, CURVE_STEEPNESS) * 100.0
    
    return err, start_rt * 100.0, end_rt * 100.0, avg_rt * 100.0, end_borrow, avg_borrow

def render():
    st.title("Adaptive Curve IRM Simulator")
    st.markdown("Simulate future IRM Kink rates from current utilization and kink rate, annualized rates with time in hours.")

    with st.sidebar:
        u_pct = st.number_input("Current Utilization (%)", min_value=0.0, max_value=100.0, value=80.0, step=0.1, help="Assumed constant during the time horizon.")
        kink_pct = st.number_input("Current IRM Kink Rate (APR, %)", min_value=0.0, max_value=1000.0, value=5.0, step=0.1, help="Annualized rate at target utilization (kink).")
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
    end_kink_rates = []
    avg_kink_rates = []
    end_borrow_rates = []
    
    for t in times:
        t_hours = float(t) if not use_days else float(t) * 24.0
        _, _, end_kink, avg_kink, end_borrow, _ = simulate(u_pct, kink_pct, t_hours)
        end_kink_rates.append(end_kink)
        avg_kink_rates.append(avg_kink)
        end_borrow_rates.append(end_borrow)

    # Styling constants
    chart_bg = "#f0f0f0"
    grid_color = "#d9d9d9"  # Muted, slightly darker than f0f0f0
    
    # --- Chart 1: Kink Rate vs Time ---
    fig_kink = go.Figure()
    fig_kink.add_trace(go.Scatter(x=times, y=end_kink_rates, mode="lines", name="End IRM Kink Rate (APR, %)", line=dict(width=3)))
    if show_avg:
        fig_kink.add_trace(go.Scatter(x=times, y=avg_kink_rates, mode="lines", name="Average IRM Kink Rate (APR, %)", line=dict(width=2, dash="dash")))
    
    fig_kink.update_layout(
        title={"text": "<span style=\"font-weight:normal\">IRM Kink Rate vs Time</span>", "x": 0.48, "xanchor": "center"},
        title_font=dict(size=22),
        height=400,
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        margin=dict(l=80, r=80, t=60, b=50)
    )
    fig_kink.update_xaxes(
        title_text=("Days" if use_days else "Hours"),
        showgrid=True,
        gridcolor=grid_color,
        gridwidth=1,
        showline=True,
        linecolor=grid_color,
        linewidth=1
    )
    fig_kink.update_yaxes(
        title_text="Rate (APR, %)",
        showgrid=True,
        gridcolor=grid_color,
        gridwidth=1,
        showline=True,
        linecolor=grid_color,
        linewidth=1
    )

    # --- Chart 2: Borrow Rate vs Time ---
    fig_borrow = go.Figure()
    fig_borrow.add_trace(go.Scatter(x=times, y=end_borrow_rates, mode="lines", name="Borrow Rate (APR, %)", line=dict(width=3, color='#FFA500')))
    
    fig_borrow.update_layout(
        title={"text": "<span style=\"font-weight:normal\">Borrow Rate vs Time</span>", "x": 0.48, "xanchor": "center"},
        title_font=dict(size=22),
        height=400,
        plot_bgcolor=chart_bg,
        paper_bgcolor=chart_bg,
        margin=dict(l=80, r=80, t=60, b=50)
    )
    fig_borrow.update_xaxes(
        title_text=("Days" if use_days else "Hours"),
        showgrid=True,
        gridcolor=grid_color,
        gridwidth=1,
        showline=True,
        linecolor=grid_color,
        linewidth=1
    )
    fig_borrow.update_yaxes(
        title_text="Borrow Rate (APR, %)",
        showgrid=True,
        gridcolor=grid_color,
        gridwidth=1,
        showline=True,
        linecolor=grid_color,
        linewidth=1
    )

    # --- Layout ---
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
        # Summary removed as requested

    with col_right:
        st.plotly_chart(fig_kink, use_container_width=True)

    st.markdown("### Borrow Rate Projection")
    st.plotly_chart(fig_borrow, use_container_width=True)

def main():
    render()

if __name__ == "__main__":
    main()
