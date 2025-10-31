#@title Multi-Curve Interest Rate Model Analyzer
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional


class InterestRateCurve:
    """
    Class to represent an interest rate curve with utilization and rate data.
    """
    def __init__(self, utilization: List[float], rates: List[float], name: str, color: str = None, marker: str = None):
        self.utilization = np.array(utilization)
        self.rates = np.array(rates)
        self.name = name
        self.color = color
        self.marker = marker
        self.interpolated_rates = None
        
    def interpolate(self, common_util: np.ndarray) -> np.ndarray:
        """Interpolate the curve to common utilization points."""
        self.interpolated_rates = np.interp(common_util, self.utilization, self.rates)
        return self.interpolated_rates


class MultiCurveIRMAnalyzer:
    """
    Multi-curve Interest Rate Model Analyzer that supports n curves with customizable options.
    """
    
    def __init__(self, show_derivatives: bool = True):
        self.curves: List[InterestRateCurve] = []
        self.show_derivatives = show_derivatives
        self.common_util = np.linspace(0, 100, 101)
        
        # Default colors and markers for curves
        self.default_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        self.default_markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
    def add_curve(self, utilization: List[float], rates: List[float], name: str, 
                  color: str = None, marker: str = None) -> None:
        """
        Add a new interest rate curve to the analyzer.
        
        Args:
            utilization: List of utilization percentages (0-100)
            rates: List of corresponding interest rates
            name: Legend name for the curve
            color: Optional color for the curve (auto-assigned if None)
            marker: Optional marker style for data points (auto-assigned if None)
        """
        curve_index = len(self.curves)
        
        # Auto-assign color and marker if not provided
        if color is None:
            color = self.default_colors[curve_index % len(self.default_colors)]
        if marker is None:
            marker = self.default_markers[curve_index % len(self.default_markers)]
            
        curve = InterestRateCurve(utilization, rates, name, color, marker)
        self.curves.append(curve)
        
    def calculate_derivatives(self, utilization: np.ndarray, rates: np.ndarray) -> np.ndarray:
        """
        Calculate the derivative (slope) of the borrow rate curve using numpy gradient.
        """
        return np.gradient(rates, utilization)
    
    def plot_curves(self, figsize: Tuple[int, int] = (14, 10), 
                   show_annotations: bool = True, annotation_offset: float = 3.0) -> None:
        """
        Plot all interest rate curves with optional derivative charts.
        
        Args:
            figsize: Figure size tuple (width, height)
            show_annotations: Whether to show value annotations on data points
            annotation_offset: Offset for annotation positioning
        """
        if not self.curves:
            print("No curves added. Please add curves using add_curve() method.")
            return
            
        # Interpolate all curves to common utilization points
        for curve in self.curves:
            curve.interpolate(self.common_util)
            
        # Determine subplot layout
        if self.show_derivatives:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(figsize[0], figsize[1]//2))
            
        # Plot 1: Interest Rate Curves
        max_rate = 0
        
        for i, curve in enumerate(self.curves):
            # Plot interpolated curves as lines
            ax1.plot(self.common_util, curve.interpolated_rates, '-', 
                    label=f'{curve.name} (interpolated)', 
                    linewidth=2, color=curve.color, alpha=0.7)
            
            # Plot original data points
            ax1.plot(curve.utilization, curve.rates, curve.marker, 
                    label=f'{curve.name} (data points)', 
                    markersize=8, color=curve.color, 
                    markerfacecolor='white', markeredgewidth=2)
            
            # Track maximum rate for y-axis scaling
            max_rate = max(max_rate, np.max(curve.interpolated_rates))
            
            # Add annotations if requested
            if show_annotations:
                self._add_annotations(ax1, curve, annotation_offset, i)
        
        # Configure main plot
        ax1.set_xlabel('Utilization Rate (%)', fontsize=12)
        ax1.set_ylabel('Borrow Rate (%)', fontsize=12)
        ax1.set_title('Interest Rate Models: Utilization vs Borrow Rate', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.set_xlim(0, 100)
        ax1.set_ylim(0, max_rate * 1.2)
        
        # Plot 2: Derivatives (if enabled)
        if self.show_derivatives:
            for curve in self.curves:
                derivatives = self.calculate_derivatives(self.common_util, curve.interpolated_rates)
                ax2.plot(self.common_util, derivatives, '-', 
                        label=f'{curve.name} Derivative', 
                        linewidth=2, color=curve.color, alpha=0.8)
            
            ax2.set_xlabel('Utilization Rate (%)', fontsize=12)
            ax2.set_ylabel('Rate of Change (% per % utilization)', fontsize=12)
            ax2.set_title('Interest Rate Model Derivatives: Rate of Change', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.set_xlim(0, 100)
        
        plt.tight_layout()
        plt.show()
        
    def _add_annotations(self, ax, curve: InterestRateCurve, offset: float, curve_index: int) -> None:
        """Add value annotations to data points."""
        for j, util_point in enumerate(curve.utilization):
            if util_point == 0:  # Skip the (0,0) point
                continue
                
            rate_value = curve.rates[j]
            
            # Alternate annotation positioning to avoid overlap
            x_offset = offset * (1 if curve_index % 2 == 0 else -1)
            y_offset = 0.5 + (curve_index * 0.3)
            
            # Choose annotation color (lighter version of curve color)
            annotation_colors = {
                'blue': 'lightblue', 'red': 'lightcoral', 'green': 'lightgreen',
                'orange': 'moccasin', 'purple': 'plum', 'brown': 'tan',
                'pink': 'lightpink', 'gray': 'lightgray', 'olive': 'khaki', 'cyan': 'lightcyan'
            }
            bg_color = annotation_colors.get(curve.color, 'lightgray')
            
            ax.annotate(f'{rate_value:.2f}%', 
                       xy=(util_point, rate_value), 
                       xytext=(util_point + x_offset, rate_value + y_offset),
                       bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color=curve.color, alpha=0.7),
                       fontsize=9, color=curve.color)
    
    def print_summary(self) -> None:
        """Print comprehensive summary statistics for all curves."""
        if not self.curves:
            print("No curves added. Please add curves using add_curve() method.")
            return
            
        print("=" * 60)
        print("MULTI-CURVE INTEREST RATE MODEL SUMMARY")
        print("=" * 60)
        
        # Print original data points for each curve
        for i, curve in enumerate(self.curves, 1):
            print(f"\n{i}. {curve.name} (Original Data Points):")
            for util, rate in zip(curve.utilization, curve.rates):
                print(f"   {util:5.1f}% utilization: {rate:6.2f}%")
        
        print("\n" + "=" * 60)
        print("INTERPOLATED VALUES AT KEY POINTS")
        print("=" * 60)
        
        # Print interpolated values at key points
        key_points = [25, 50, 75, 90, 95]
        for point in key_points:
            print(f"\nAt {point}% utilization:")
            for curve in self.curves:
                if curve.interpolated_rates is not None:
                    rate_at_point = curve.interpolated_rates[point]
                    print(f"   {curve.name:20}: {rate_at_point:6.2f}%")
        
        print("\n" + "=" * 60)
        print("CURVE STATISTICS")
        print("=" * 60)
        
        for curve in self.curves:
            if curve.interpolated_rates is not None:
                max_rate = np.max(curve.interpolated_rates)
                min_rate = np.min(curve.interpolated_rates)
                avg_rate = np.mean(curve.interpolated_rates)
                
                print(f"\n{curve.name}:")
                print(f"   Max Rate: {max_rate:6.2f}%")
                print(f"   Min Rate: {min_rate:6.2f}%")
                print(f"   Avg Rate: {avg_rate:6.2f}%")
                
                # Calculate derivative statistics
                derivatives = self.calculate_derivatives(self.common_util, curve.interpolated_rates)
                max_slope = np.max(derivatives)
                avg_slope = np.mean(derivatives)
                
                print(f"   Max Slope: {max_slope:6.3f}% per % utilization")
                print(f"   Avg Slope: {avg_slope:6.3f}% per % utilization")


def main():
    """
    Main function demonstrating the multi-curve analyzer with example data.
    """
    # Configuration: Set whether to show derivative charts
    SHOW_DERIVATIVES = False  # Set to False to hide derivative charts
    
    # Initialize the analyzer
    analyzer = MultiCurveIRMAnalyzer(show_derivatives=SHOW_DERIVATIVES)
    
    # # PYUSD Current Model
    # analyzer.add_curve(
    #     utilization=[0, 25, 95, 100],
    #     rates=[5.7, 8.35, 53.2, 73],
    #     name="PYUSD Current",
    #     color="blue"
    # )
    
    # # USDC Current Model
    # analyzer.add_curve(
    #     utilization=[0, 80, 90, 100],
    #     rates=[0, 3.64, 5.59, 14.72],
    #     name="USDC Current",
    #     color="red"
    # )
    
    # # Recommendation
    # analyzer.add_curve(
    #     utilization=[0, 40, 60, 100],
    #     rates=[2, 5.5, 9, 50],
    #     name="Recommendation Model",
    #     color="green"
    # )

    # Recommendation
    analyzer.add_curve(
        utilization=[0, 40, 50, 60, 100],
        rates=[3.5, 5.5, 6.5, 8.5, 20.5],
        name="Phase 3",
        color="black"
    )

    # Recommendation
    analyzer.add_curve(
        utilization=[0, 25, 35, 45, 100],
        rates=[4.25, 5.5, 6.5, 8.5, 25],
        name="Phase 2",
        color="orange"
    )

    # Recommendation
    analyzer.add_curve(
        utilization=[0, 10, 20, 30, 100],
        rates=[5, 5.5, 6.5, 8.5, 29.5],
        name="Phase 1",
        color="green"
    )
    
    # # Recommendation
    # analyzer.add_curve(
    #     utilization=[0, 80, 90, 100],
    #     rates=[0, 3.8, 5.9, 17],
    #     name="Recommendation IRM PYUSD",
    #     color="green"
    # )
    
    # Plot all curves
    print("Plotting interest rate curves...")
    analyzer.plot_curves(
        figsize=(14, 12 if SHOW_DERIVATIVES else 8),
        show_annotations=True,
        annotation_offset=2.5
    )
    
    # Print comprehensive summary
    analyzer.print_summary()


if __name__ == "__main__":
    main()