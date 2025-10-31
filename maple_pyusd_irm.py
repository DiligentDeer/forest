#@title Interest Rate Model - Maple PYUSD IRM Analysis
import numpy as np
import matplotlib.pyplot as plt


def calculate_derivatives(utilization, borrow_rate):
    """
    Calculate the derivative (slope) of the borrow rate curve using numpy gradient.
    """
    # Use numpy's gradient function for smooth derivative calculation
    # This calculates the discrete difference along the given axis
    derivatives = np.gradient(borrow_rate, utilization)
    
    return derivatives

def plot_interest_rate_models(common_util, reference_interp, curve_1_interp, 
                             reference_util, reference_borrow_rate, util_1, borrow_rate_1):
    """
    Plot the interest rate curves and their derivatives.
    """
    # Calculate derivatives for interpolated curves
    derivatives_ref = calculate_derivatives(common_util, reference_interp)
    derivatives_1 = calculate_derivatives(common_util, curve_1_interp)
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Interest Rate Curves
    # Plot interpolated curves as lines
    ax1.plot(common_util, reference_interp, '-', label='Reference Model (interpolated)', 
             linewidth=2, color='blue', alpha=0.7)
    ax1.plot(common_util, curve_1_interp, '-', label='Custom Model (interpolated)', 
             linewidth=2, color='red', alpha=0.7)
    
    # Plot original data points
    ax1.plot(reference_util, reference_borrow_rate, 'o', label='Reference Model (data points)', 
             markersize=6, color='blue', markerfacecolor='white', markeredgewidth=2)
    ax1.plot(util_1, borrow_rate_1, 's', label='Custom Model (data points)', 
             markersize=6, color='red', markerfacecolor='white', markeredgewidth=2)
    
    # Add annotations at custom model utilization points (skip 0,0 point)
    for util_point in util_1:
        if util_point == 0:  # Skip the (0,0) point
            continue
            
        # Get interpolated values for both models at this utilization point
        ref_rate = np.interp(util_point, reference_util, reference_borrow_rate)
        custom_rate = np.interp(util_point, util_1, borrow_rate_1)
        
        # Add annotation for reference model
        ax1.annotate(f'{ref_rate:.2f}%', 
                    xy=(util_point, ref_rate), 
                    xytext=(util_point + 3, ref_rate + 0.5),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7),
                    fontsize=9, color='blue')
        
        # Add annotation for custom model
        ax1.annotate(f'{custom_rate:.2f}%', 
                    xy=(util_point, custom_rate), 
                    xytext=(util_point - 8, custom_rate + 0.5),
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7),
                    arrowprops=dict(arrowstyle='->', color='red', alpha=0.7),
                    fontsize=9, color='red')
    
    ax1.set_xlabel('Utilization Rate (%)')
    ax1.set_ylabel('Borrow Rate (%)')
    ax1.set_title('Interest Rate Models: Utilization vs Borrow Rate')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(0, 100)
    ax1.set_ylim(0, max(max(reference_interp), max(curve_1_interp)) * 1.2)
    
    # Plot 2: Derivatives (Rate of Change)
    ax2.plot(common_util, derivatives_ref, '-', label='Reference Model Derivative', 
             linewidth=2, color='blue', alpha=0.8)
    ax2.plot(common_util, derivatives_1, '-', label='Custom Model Derivative', 
             linewidth=2, color='red', alpha=0.8)
    
    ax2.set_xlabel('Utilization Rate (%)')
    ax2.set_ylabel('Rate of Change (% per % utilization)')
    ax2.set_title('Interest Rate Model Derivatives: Rate of Change')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_xlim(0, 100)
    
    plt.tight_layout()
    plt.show()

def print_model_summary(common_util, reference_interp, curve_1_interp, 
                       reference_util, reference_borrow_rate, util_1, borrow_rate_1):
    """
    Print summary statistics for both models.
    """
    print("=== Interest Rate Model Summary ===\n")
    
    print("Reference Model (Original Data Points):")
    for i, (util, rate) in enumerate(zip(reference_util, reference_borrow_rate)):
        print(f"  {util}% utilization: {rate:.2f}%")
    
    print("\nCustom Model (Original Data Points):")
    for i, (util, rate) in enumerate(zip(util_1, borrow_rate_1)):
        print(f"  {util}% utilization: {rate:.2f}%")
    
    print("\nInterpolated Values at Key Points:")
    print("Reference Model:")
    print(f"  Rate at 50% utilization: {reference_interp[50]:.2f}%")
    print(f"  Rate at 75% utilization: {reference_interp[75]:.2f}%")
    print(f"  Rate at 95% utilization: {reference_interp[95]:.2f}%")
    print(f"  Max Rate: {max(reference_interp):.2f}%")
    
    print("\nCustom Model:")
    print(f"  Rate at 50% utilization: {curve_1_interp[50]:.2f}%")
    print(f"  Rate at 75% utilization: {curve_1_interp[75]:.2f}%")
    print(f"  Rate at 95% utilization: {curve_1_interp[95]:.2f}%")
    print(f"  Max Rate: {max(curve_1_interp):.2f}%")
    
    # Calculate derivatives for analysis
    derivatives_ref = calculate_derivatives(common_util, reference_interp)
    derivatives_1 = calculate_derivatives(common_util, curve_1_interp)
    
    print(f"\nDerivative Analysis:")
    print(f"  Reference model max slope: {max(derivatives_ref):.3f}% per % utilization")
    print(f"  Custom model max slope: {max(derivatives_1):.3f}% per % utilization")

def main():
    """
    Main function to run the interest rate model analysis.
    """
    # Custom input arrays as specified by the user
    # reference_util = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    # reference_borrow_rate = [0, 0.45, 0.9, 1.35, 1.8, 2.26, 2.72, 3.18, 3.64, 5.59, 14.72]

    # PYUSD Current
    reference_util = [0, 25, 95, 100]
    reference_borrow_rate = [5.7, 8.35, 53.2, 73]

    # reference_util = [0, 85, 95, 100]
    # reference_borrow_rate = [0, 4.1, 6.8, 27]
    
    # util_1 = [0, 60, 70, 80, 90, 100]
    # borrow_rate_1 = [0, 2.72, 3.25, 3.9, 6.2, 17]
    
    # util_1 = [0, 80, 90, 100]
    # borrow_rate_1 = [0, 3.8, 5.9, 17]

    util_1 = [0, 95, 100]
    borrow_rate_1 = [0, 6.16, 45.9]
    
    # Create common utilization range for interpolation
    common_util = np.linspace(0, 100, 101)
    
    # Interpolate both curves to common utilization points
    reference_interp = np.interp(common_util, reference_util, reference_borrow_rate)
    curve_1_interp = np.interp(common_util, util_1, borrow_rate_1)
    
    # Plot the models
    plot_interest_rate_models(common_util, reference_interp, curve_1_interp,
                            reference_util, reference_borrow_rate, util_1, borrow_rate_1)
    
    # Print summary
    print_model_summary(common_util, reference_interp, curve_1_interp,
                       reference_util, reference_borrow_rate, util_1, borrow_rate_1)

if __name__ == "__main__":
    main()