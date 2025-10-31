#@title Borrow & Supply Rate Analyzer
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional


class BorrowSupplyRateCurve:
    """
    Class to represent borrow and supply rate curves with utilization data.
    """
    def __init__(self, utilization: List[float], borrow_rates: List[float], name: str, 
                 take_rate: float, color: str = None, marker: str = None):
        self.utilization = np.array(utilization)
        self.borrow_rates = np.array(borrow_rates)
        self.name = name
        self.take_rate = take_rate
        self.color = color
        self.marker = marker
        
        # Calculate supply rates using the formula: supply_rate = utilization * borrow_rate * (1 - take_rate)
        # Convert utilization from percentage to decimal for calculation
        self.supply_rates = (self.utilization / 100) * self.borrow_rates * (1 - take_rate)
        
        # Interpolated curves
        self.interpolated_borrow_rates = None
        self.interpolated_supply_rates = None
        
    def interpolate(self, common_util: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Interpolate both borrow and supply curves to common utilization points."""
        self.interpolated_borrow_rates = np.interp(common_util, self.utilization, self.borrow_rates)
        
        # Calculate interpolated supply rates using the formula
        self.interpolated_supply_rates = (common_util / 100) * self.interpolated_borrow_rates * (1 - self.take_rate)
        
        return self.interpolated_borrow_rates, self.interpolated_supply_rates


class BorrowSupplyRateAnalyzer:
    """
    Analyzer for plotting both borrow and supply rate curves with customizable take rate.
    """
    
    def __init__(self, take_rate: float = 0.1, show_derivatives: bool = True, max_utilization: float = 100.0):
        self.curves: List[BorrowSupplyRateCurve] = []
        self.take_rate = take_rate
        self.show_derivatives = show_derivatives
        self.max_utilization = max(0.0, min(100.0, max_utilization))  # Clamp between 0 and 100
        self.common_util = np.linspace(0, self.max_utilization, int(self.max_utilization) + 1)
        
        # Default colors and markers for curves
        self.default_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        self.default_markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
        
    def add_curve(self, utilization: List[float], rates: List[float], name: str, 
                  color: str = None, marker: str = None) -> None:
        """
        Add a new borrow rate curve to the analyzer. Supply rates will be calculated automatically.
        
        Args:
            utilization: List of utilization percentages (0-100)
            rates: List of corresponding borrow interest rates
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
            
        curve = BorrowSupplyRateCurve(utilization, rates, name, self.take_rate, color, marker)
        self.curves.append(curve)
        
    def calculate_derivatives(self, utilization: np.ndarray, rates: np.ndarray) -> np.ndarray:
        """
        Calculate the derivative (slope) of the rate curve using numpy gradient.
        """
        return np.gradient(rates, utilization)
    
    def plot_curves(self, figsize: Tuple[int, int] = (16, 12), 
                   show_annotations: bool = True, annotation_offset: float = 3.0) -> None:
        """
        Plot both borrow and supply rate curves on the same chart with optional derivative charts.
        
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
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(figsize[0]//2, figsize[1]//2))
            
        # Plot: Combined Borrow and Supply Rate Curves
        max_rate = 0
        
        for i, curve in enumerate(self.curves):
            # Plot interpolated borrow curves as solid lines
            ax1.plot(self.common_util, curve.interpolated_borrow_rates, '-', 
                    label=f'{curve.name} Borrow', 
                    linewidth=3, color=curve.color, alpha=0.8)
            
            # Plot interpolated supply curves as dashed lines
            ax1.plot(self.common_util, curve.interpolated_supply_rates, '--', 
                    label=f'{curve.name} Supply', 
                    linewidth=3, color=curve.color, alpha=0.8)
            
            # Plot original borrow data points
            ax1.plot(curve.utilization, curve.borrow_rates, curve.marker, 
                    markersize=10, color=curve.color, 
                    markerfacecolor='white', markeredgewidth=3)
            
            # Plot original supply data points
            ax1.plot(curve.utilization, curve.supply_rates, curve.marker, 
                    markersize=8, color=curve.color, 
                    markerfacecolor=curve.color, markeredgewidth=2, alpha=0.7)
            
            # Track maximum rate for y-axis scaling
            max_rate = max(max_rate, np.max(curve.interpolated_borrow_rates))
            max_rate = max(max_rate, np.max(curve.interpolated_supply_rates))
            
            # Add annotations if requested
            if show_annotations:
                self._add_annotations(ax1, curve.utilization, curve.borrow_rates, 
                                    curve.color, curve.name, annotation_offset, i, "Borrow")
                self._add_annotations(ax1, curve.utilization, curve.supply_rates, 
                                    curve.color, curve.name, annotation_offset, i, "Supply")
        
        # Configure combined rate plot
        ax1.set_xlabel('Utilization Rate (%)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Interest Rate (%)', fontsize=14, fontweight='bold')
        title = f'Borrow & Supply Rate Models (Take Rate: {self.take_rate*100:.1f}%)'
        if self.max_utilization < 100:
            title += f'\nUtilization Range: 0% - {self.max_utilization:.0f}%'
        ax1.set_title(title, fontsize=16, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
        ax1.set_xlim(0, self.max_utilization)
        ax1.set_ylim(0, max_rate * 1.2)
        
        # Add text box explaining line styles
        textstr = 'Solid lines: Borrow Rates\nDashed lines: Supply Rates\nCircles: Borrow Data Points\nFilled circles: Supply Data Points'
        props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
        ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
        
        # Plot 2: Derivatives (if enabled)
        if self.show_derivatives:
            # Combined derivatives plot
            for curve in self.curves:
                # Borrow rate derivatives
                borrow_derivatives = self.calculate_derivatives(self.common_util, curve.interpolated_borrow_rates)
                ax2.plot(self.common_util, borrow_derivatives, '-', 
                        label=f'{curve.name} Borrow Derivative', 
                        linewidth=3, color=curve.color, alpha=0.8)
                
                # Supply rate derivatives
                supply_derivatives = self.calculate_derivatives(self.common_util, curve.interpolated_supply_rates)
                ax2.plot(self.common_util, supply_derivatives, '--', 
                        label=f'{curve.name} Supply Derivative', 
                        linewidth=3, color=curve.color, alpha=0.8)
            
            ax2.set_xlabel('Utilization Rate (%)', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Rate Change (% per % utilization)', fontsize=14, fontweight='bold')
            derivative_title = 'Rate Derivatives'
            if self.max_utilization < 100:
                derivative_title += f' (0% - {self.max_utilization:.0f}%)'
            ax2.set_title(derivative_title, fontsize=16, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=11)
            ax2.set_xlim(0, self.max_utilization)
            
            # Add text box explaining line styles for derivatives
            textstr = 'Solid lines: Borrow Rate Derivatives\nDashed lines: Supply Rate Derivatives'
            props = dict(boxstyle='round', facecolor='lightgray', alpha=0.8)
            ax2.text(0.02, 0.98, textstr, transform=ax2.transAxes, fontsize=10,
                    verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plt.show()
        
    def _add_annotations(self, ax, utilization: np.ndarray, rates: np.ndarray, 
                        color: str, name: str, offset: float, curve_index: int, rate_type: str) -> None:
        """Add value annotations to data points."""
        for j, util_point in enumerate(utilization):
            if util_point == 0 and rate_type == "Supply":  # Skip the (0,0) point for supply rates
                continue
                
            rate_value = rates[j]
            
            # Adjust positioning based on rate type to avoid overlap
            if rate_type == "Borrow":
                x_offset = offset * (1 if curve_index % 2 == 0 else -1)
                y_offset = 0.5 + (curve_index * 0.3)
            else:  # Supply rates
                x_offset = offset * (-1 if curve_index % 2 == 0 else 1)  # Opposite side from borrow
                y_offset = -0.8 - (curve_index * 0.3)  # Below the point
            
            # Choose annotation color and style based on rate type
            annotation_colors = {
                'blue': 'lightblue', 'red': 'lightcoral', 'green': 'lightgreen',
                'orange': 'moccasin', 'purple': 'plum', 'brown': 'tan',
                'pink': 'lightpink', 'gray': 'lightgray', 'olive': 'khaki', 'cyan': 'lightcyan'
            }
            bg_color = annotation_colors.get(color, 'lightgray')
            
            # Different styling for borrow vs supply annotations
            if rate_type == "Borrow":
                box_style = "round,pad=0.3"
                font_weight = 'bold'
            else:
                box_style = "round,pad=0.2"
                font_weight = 'normal'
            
            ax.annotate(f'{rate_type[0]}: {rate_value:.2f}%',  # B: or S: prefix
                       xy=(util_point, rate_value), 
                       xytext=(util_point + x_offset, rate_value + y_offset),
                       bbox=dict(boxstyle=box_style, facecolor=bg_color, alpha=0.8),
                       arrowprops=dict(arrowstyle='->', color=color, alpha=0.8),
                       fontsize=8, color=color, weight=font_weight)
    
    def print_summary(self) -> None:
        """Print comprehensive summary statistics for all curves."""
        if not self.curves:
            print("No curves added. Please add curves using add_curve() method.")
            return
            
        print("=" * 80)
        print("BORROW & SUPPLY RATE MODEL SUMMARY")
        print(f"Take Rate: {self.take_rate*100:.1f}%")
        print("=" * 80)
        
        # Print original data points for each curve
        for i, curve in enumerate(self.curves, 1):
            print(f"\n{i}. {curve.name} (Original Data Points):")
            print("   Utilization | Borrow Rate | Supply Rate")
            print("   ------------|-------------|------------")
            for util, borrow, supply in zip(curve.utilization, curve.borrow_rates, curve.supply_rates):
                print(f"   {util:8.1f}%   | {borrow:8.2f}%   | {supply:8.2f}%")
        
        print("\n" + "=" * 80)
        print("INTERPOLATED VALUES AT KEY POINTS")
        print("=" * 80)
        
        # Print interpolated values at key points (only within max_utilization range)
        all_key_points = [25, 50, 75, 90, 95]
        key_points = [point for point in all_key_points if point <= self.max_utilization]
        
        for point in key_points:
            print(f"\nAt {point}% utilization:")
            print("   Model Name           | Borrow Rate | Supply Rate")
            print("   ---------------------|-------------|------------")
            for curve in self.curves:
                if curve.interpolated_borrow_rates is not None:
                    borrow_at_point = curve.interpolated_borrow_rates[point]
                    supply_at_point = curve.interpolated_supply_rates[point]
                    print(f"   {curve.name:20} | {borrow_at_point:8.2f}%   | {supply_at_point:8.2f}%")
        
        print("\n" + "=" * 80)
        print("CURVE STATISTICS")
        print("=" * 80)
        
        for curve in self.curves:
            if curve.interpolated_borrow_rates is not None:
                # Borrow rate statistics
                max_borrow = np.max(curve.interpolated_borrow_rates)
                min_borrow = np.min(curve.interpolated_borrow_rates)
                avg_borrow = np.mean(curve.interpolated_borrow_rates)
                
                # Supply rate statistics
                max_supply = np.max(curve.interpolated_supply_rates)
                min_supply = np.min(curve.interpolated_supply_rates)
                avg_supply = np.mean(curve.interpolated_supply_rates)
                
                print(f"\n{curve.name}:")
                print(f"   Borrow Rates - Max: {max_borrow:6.2f}%, Min: {min_borrow:6.2f}%, Avg: {avg_borrow:6.2f}%")
                print(f"   Supply Rates - Max: {max_supply:6.2f}%, Min: {min_supply:6.2f}%, Avg: {avg_supply:6.2f}%")
                
                # Calculate derivative statistics
                borrow_derivatives = self.calculate_derivatives(self.common_util, curve.interpolated_borrow_rates)
                supply_derivatives = self.calculate_derivatives(self.common_util, curve.interpolated_supply_rates)
                
                max_borrow_slope = np.max(borrow_derivatives)
                max_supply_slope = np.max(supply_derivatives)
                
                print(f"   Max Borrow Slope: {max_borrow_slope:6.3f}% per % utilization")
                print(f"   Max Supply Slope: {max_supply_slope:6.3f}% per % utilization")
                
                # Calculate spread at different utilization levels (only within max_utilization range)
                spread_points = [point for point in [50, 90] if point <= self.max_utilization]
                for point in spread_points:
                    print(f"   Borrow-Supply Spread at {point}%: {curve.interpolated_borrow_rates[point] - curve.interpolated_supply_rates[point]:.2f}%")


def main():
    """
    Main function demonstrating the borrow-supply rate analyzer with example data.
    """
    # Configuration: Set take rate and whether to show derivative charts
    TAKE_RATE = 0.1  # 10% take rate
    SHOW_DERIVATIVES = False  # Set to True to show derivative charts
    MAX_UTILIZATION = 70  # Maximum utilization to display (clips x-axis)
    
    # Initialize the analyzer with custom max utilization
    # This will clip the chart to show only 0% to MAX_UTILIZATION%
    # Change MAX_UTILIZATION to any value between 0-100 to adjust the x-axis range
    analyzer = BorrowSupplyRateAnalyzer(take_rate=TAKE_RATE, show_derivatives=SHOW_DERIVATIVES, max_utilization=MAX_UTILIZATION)
    
    # # Example 1: USDC Current Model (from user's example)
    # analyzer.add_curve(
    #     utilization=[0, 95, 100],
    #     rates=[0, 6.16, 45.9],
    #     name="USDC Current",
    #     color="red"
    # )
    
    # # Example 2: PYUSD Model
    # analyzer.add_curve(
    #     utilization=[0, 25, 95, 100],
    #     rates=[5.7, 8.35, 53.2, 73],
    #     name="PYUSD Current",
    #     color="blue"
    # )
    
    # # Recommendation
    # analyzer.add_curve(
    #     utilization=[0, 40, 60, 100],
    #     rates=[2, 5.5, 9, 50],
    #     name="Recommendation Model",
    #     color="green"
    # )

    # # Recommendation
    # analyzer.add_curve(
    #     utilization=[0, 80, 90, 100],
    #     rates=[0, 3.8, 5.9, 17],
    #     name="Recommendation IRM PYUSD",
    #     color="green"
    # )

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
    
    # Plot all curves
    print(f"Plotting borrow and supply rate curves with {TAKE_RATE*100:.1f}% take rate...")
    analyzer.plot_curves(
        figsize=(16, 12 if SHOW_DERIVATIVES else 8),
        show_annotations=True,
        annotation_offset=2.0
    )
    
    # Print comprehensive summary
    analyzer.print_summary()


if __name__ == "__main__":
    main()