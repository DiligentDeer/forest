import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

def calculate_price_changes(input_mode, initial_value, final_value):
    """Calculate price changes based on input mode (HF or LTV)"""
    if input_mode == 'hf':
        # Health Factor mode
        ratio = initial_value / final_value
        hf_decreased = final_value < initial_value
    else:
        # LTV mode
        ratio = final_value / initial_value
        hf_decreased = final_value > initial_value  # Higher LTV means lower HF
    
    # Isolated changes
    debt_change = (ratio - 1) * 100  # Debt price change %
    collateral_change = (1 - 1/ratio) * 100  # Collateral price change %
    
    # Apply correct signs based on HF direction
    if hf_decreased:
        # HF decreased: debt increased (+) or collateral decreased (-)
        debt_only = abs(debt_change)  # Positive (increase)
        collateral_only = -abs(collateral_change)  # Negative (decrease)
    else:
        # HF increased: debt decreased (-) or collateral increased (+)
        debt_only = -abs(debt_change)  # Negative (decrease)
        collateral_only = abs(collateral_change)  # Positive (increase)
    
    return ratio, debt_only, collateral_only, hf_decreased

def generate_combined_scenarios(ratio, max_debt_increase=100):
    """Generate data for combined price movement scenarios"""
    data = []
    
    for debt_increase in np.linspace(0, max_debt_increase, 101):
        alpha = debt_increase / 100
        beta = 1 - (1 + alpha) / ratio
        collateral_decrease = beta * 100
        
        # Only include valid scenarios (positive collateral decrease, within reasonable bounds)
        if 0 <= collateral_decrease <= 100:
            data.append({
                'debt_increase': debt_increase,
                'collateral_decrease': collateral_decrease
            })
    
    return pd.DataFrame(data)

def render():
    """Render the Loan Liquidation Risk Calculator page"""
    st.title("Loan Liquidation Risk Calculator")
    st.markdown("Analyze how debt and collateral price movements affect your loan health and liquidation risk.")
    
    # Sidebar controls - Single column layout
    st.sidebar.markdown("### Input Parameters")
    
    # Input mode selection
    input_mode = st.sidebar.radio(
        "Input Mode:",
        ["hf", "ltv"],
        format_func=lambda x: "Health Factor" if x == "hf" else "LTV Ratio",
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # Single column layout for parameters
    if input_mode == 'hf':
        initial_hf = st.sidebar.slider(
            "Initial Health Factor:",
            min_value=0.5,
            max_value=3.0,
            value=1.5,
            step=0.1,
            format="%.1f"
        )
        
        final_hf = st.sidebar.slider(
            "Final Health Factor:",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.1,
            format="%.1f"
        )
        
        initial_value, final_value = initial_hf, final_hf
        
    else:  # LTV mode
         initial_ltv = st.sidebar.slider(
             "Initial LTV:",
             min_value=0,
             max_value=150,
             value=60,
             step=1,
             format="%d%%",
             help="Initial Loan-to-Value ratio"
         ) 
         
         final_ltv = st.sidebar.slider(
             "Final LTV:",
             min_value=0,
             max_value=150,
             value=85,
             step=1,
             format="%d%%",
             help="Final Loan-to-Value ratio"
         )
         
         # Convert percentage values to decimal for calculations
         initial_value, final_value = initial_ltv / 100, final_ltv / 100
    
    st.sidebar.markdown("---")
    
    # Calculate price changes
    ratio, debt_only, collateral_only, hf_decreased = calculate_price_changes(input_mode, initial_value, final_value)
    
    # Risk assessment
    if input_mode == 'hf':
        is_liquidatable = final_value < 1.0
        risk_message = "Warning: This position is liquidatable (HF < 1)" if is_liquidatable else "Position is safe from liquidation"
    else:
        # For LTV mode, assume LLTV threshold around 0.9 (90%)
        is_liquidatable = final_value > 0.9
        risk_message = "Warning: This position may be close to liquidation" if is_liquidatable else "Position appears safe"
    
    if is_liquidatable:
        st.sidebar.error(risk_message)
    else:
        st.sidebar.success(risk_message)
    
    # Main content area - Compact metrics section
    st.markdown("### Key Metrics")
    
    # Create 4 columns for compact layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if input_mode == 'hf':
            st.metric(
                "Initial HF", 
                f"{initial_value:.2f}",
                help="Health Factor = LLTV / LTV. Values > 1 are safe from liquidation."
            )
        else:
            st.metric(
                "Initial LTV", 
                f"{initial_value*100:.0f}%",
                help="Loan-to-Value = (Debt × Debt_Price) / (Collateral × Collateral_Price)"
            )
    
    with col2:
        if input_mode == 'hf':
            st.metric(
                "Final HF", 
                f"{final_value:.2f}",
                help="Target Health Factor after price movements."
            )
        else:
            st.metric(
                "Final LTV", 
                f"{final_value*100:.0f}%",
                help="Target LTV after price movements."
            )
    
    with col3:
        change_pct = ((final_value/initial_value - 1) * 100)
        st.metric(
            f"{'HF' if input_mode == 'hf' else 'LTV'} Change", 
            f"{change_pct:+.1f}%",
            help=f"Percentage change from initial to final {'Health Factor' if input_mode == 'hf' else 'LTV'}."
        )
    
    with col4:
        st.metric(
            "Price Ratio", 
            f"{ratio:.4f}",
            help="Mathematical ratio used in formula: (1 + α) / (1 + β) where α=debt change, β=collateral change."
        )
    
    # Isolated price changes section
    st.markdown("---")
    st.markdown("### Isolated Price Changes")
    st.markdown("*How much each token price must change independently:*")
    
    col1, col2 = st.columns(2)
    
    with col1:
        debt_sign = "+" if debt_only >= 0 else ""
        st.metric(
            label="Debt Token Price Change",
            value=f"{debt_sign}{debt_only:.2f}%",
            help="Required debt token price change (holding collateral price constant). Formula: α = (ratio - 1) × 100%"
        )
    
    with col2:
        collateral_sign = "+" if collateral_only >= 0 else ""
        st.metric(
            label="Collateral Token Price Change",
            value=f"{collateral_sign}{collateral_only:.2f}%",
            help="Required collateral token price change (holding debt price constant). Formula: β = (1 - 1/ratio) × 100%"
        )
    
    # Mathematical relationship
    st.markdown("---")
    st.markdown("**Mathematical Relationship:**")
    st.code(f"(1 + α) / (1 + β) = {ratio:.4f}")
    st.caption("where α = debt price change (decimal), β = collateral price change (decimal)")
    
    # Combined scenarios chart
    st.markdown("---")
    st.markdown("### Combined Price Movement Scenarios")
    st.markdown("*All combinations of debt price increases and collateral price decreases that achieve the target change:*")
    
    # Generate scenario data
    scenario_data = generate_combined_scenarios(ratio)
    
    if not scenario_data.empty:
        # Create area chart with Streamlit background color
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=scenario_data['debt_increase'],
            y=scenario_data['collateral_decrease'],
            fill='tonexty',
            mode='lines',
            name='Valid Scenarios',
            line=dict(color='#f97316', width=2),
            fillcolor='rgba(249, 115, 22, 0.3)'
        ))
        
        # Add key points
        fig.add_trace(go.Scatter(
            x=[0, abs(debt_only)],
            y=[abs(collateral_only), 0],
            mode='markers',
            name='Isolated Changes',
            marker=dict(size=10, color=['red', 'orange'], symbol=['circle', 'square'])
        ))
        
        fig.update_layout(
            title="Price Movement Combinations",
            xaxis_title="Debt Token Price Increase (%)",
            yaxis_title="Collateral Token Price Decrease (%)",
            height=500,
            showlegend=True,
            hovermode='x unified',
            plot_bgcolor='#f0f0f0',  # Light gray background color
            paper_bgcolor='#f0f0f0',  # Light gray background color
            font=dict(color='black'),
            xaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.3)',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='rgba(128, 128, 128, 0.5)',
                zerolinewidth=1
            ),
            yaxis=dict(
                gridcolor='rgba(128, 128, 128, 0.3)',
                gridwidth=1,
                zeroline=True,
                zerolinecolor='rgba(128, 128, 128, 0.5)',
                zerolinewidth=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Starting Point", 
                "Debt: 0%, Collateral: 0%",
                help="No price changes from initial state."
            )
        
        with col2:
            st.metric(
                "Max Debt Only", 
                f"{debt_only:+.1f}%",
                help="Maximum debt price change needed if collateral price stays constant."
            )
        
        with col3:
            st.metric(
                "Max Collateral Only", 
                f"{collateral_only:+.1f}%",
                help="Maximum collateral price change needed if debt price stays constant."
            )
        
        # Data export
        st.markdown("---")
        st.markdown("### Export Data")
        
        if st.button("Show Scenario Data"):
            st.dataframe(scenario_data.round(2), use_container_width=True)
        
        # CSV download
        csv = scenario_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"liquidation_scenarios_{input_mode}.csv",
            mime="text/csv"
        )
    
    else:
        st.warning("No valid combined scenarios found for the given parameters.")
    
    # Usage guide
    with st.expander("How to Use This Tool"):
        st.markdown("""
        **1. Choose Input Mode:** Select whether to work with Health Factor or LTV ratios.
        
        **2. Set Parameters:** Use the sliders to set your initial and target values.
        
        **3. Interpret Results:**
        - **Isolated Changes:** Shows how much each token price must change independently
        - **Combined Scenarios:** The chart shows all valid combinations where both prices move adversely
        - Any point on the curve represents a scenario that achieves the target HF/LTV
        
        **4. Risk Assessment:** Monitor the warning indicators for liquidation risk.
        
        **Key Formulas:**
        - Health Factor: `HF = LLTV / LTV`
        - LTV: `LTV = (Debt × Debt_Price) / (Collateral × Collateral_Price)`
        - Combined: `(1 + α) / (1 + β) = HF₀ / HF₁` (for HF mode)
        - Combined: `(1 + α) / (1 + β) = LTV₁ / LTV₀` (for LTV mode)
        """)