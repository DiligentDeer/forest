I'll help you derive the mathematical formulas and create an interactive visualization tool. Let me break this down systematically.

## Mathematical Derivations

### Setup and Definitions

Given:
- **LLTV** = Liquidation Loan-to-Value ratio (constant threshold)
- **LTV** = Current Loan-to-Value ratio = (Debt_qty × Debt_price) / (Collateral_qty × Collateral_price)
- **HF** = Health Factor = LLTV / LTV
- **Liquidation condition**: HF < 1

Let me denote:
- Initial state: debt price = P_d, collateral price = P_c
- Final state: debt price = P_d', collateral price = P_c'
- Price changes: 
  - α = % change in debt price = (P_d' - P_d) / P_d
  - β = % change in collateral price = (P_c' - P_c) / P_c

### 1. From Initial and Final Health Factor

**Given**: HF₀ (initial) and HF₁ (final)

Since HF = LLTV / LTV and LTV = (Q_d × P_d) / (Q_c × P_c), we have:

```
LTV = (Q_d × P_d) / (Q_c × P_c)
LTV' = (Q_d × P_d') / (Q_c × P_c')
```

The ratio of LTVs:
```
LTV' / LTV = (P_d' / P_d) × (P_c / P_c') = (1 + α) / (1 + β)
```

Since HF = LLTV / LTV:
```
HF₁ / HF₀ = LTV₀ / LTV₁ = (1 + β) / (1 + α)
```

**Formulas:**

**For debt price increase (holding collateral price constant, β = 0):**
```
α = (HF₀ / HF₁) - 1
α% = [(HF₀ / HF₁) - 1] × 100%
```

**For collateral price decrease (holding debt price constant, α = 0):**
```
β = (HF₁ / HF₀) - 1 = 1 - (HF₁ / HF₀)
β% = [1 - (HF₁ / HF₀)] × 100%
```

**General relationship (both prices change):**
```
(1 + α) / (1 + β) = HF₀ / HF₁
```

### 2. From Initial and Final LTV

**Given**: LTV₀ (initial) and LTV₁ (final)

Using the same logic:
```
LTV₁ / LTV₀ = (1 + α) / (1 + β)
```

**Formulas:**

**For debt price increase only (β = 0):**
```
α = (LTV₁ / LTV₀) - 1
α% = [(LTV₁ / LTV₀) - 1] × 100%
```

**For collateral price decrease only (α = 0):**
```
β = 1 - (LTV₀ / LTV₁)
β% = [1 - (LTV₀ / LTV₁)] × 100%
```

**General relationship:**
```
(1 + α) / (1 + β) = LTV₁ / LTV₀
```

### 3. Interactive Visualization

Now let me create an interactive tool that plots all combinations of debt price increases and collateral price decreases:## User Intent and Usage Guide

```javascript
import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { AlertCircle, TrendingUp, TrendingDown, Activity } from 'lucide-react';

const LoanLiquidationAnalyzer = () => {
  const [inputMode, setInputMode] = useState('hf');
  const [initialHF, setInitialHF] = useState(1.5);
  const [finalHF, setFinalHF] = useState(1.0);
  const [initialLTV, setInitialLTV] = useState(0.6);
  const [finalLTV, setFinalLTV] = useState(0.9);

  const calculations = useMemo(() => {
    let ratio;
    if (inputMode === 'hf') {
      ratio = initialHF / finalHF;
    } else {
      ratio = finalLTV / initialLTV;
    }

    const debtOnly = ((ratio - 1) * 100).toFixed(2);
    const collateralOnly = ((1 - 1/ratio) * 100).toFixed(2);

    const data = [];
    for (let debtIncrease = 0; debtIncrease <= 100; debtIncrease += 1) {
      const alpha = debtIncrease / 100;
      const beta = 1 - (1 + alpha) / ratio;
      const collateralDecrease = beta * 100;
      
      if (collateralDecrease >= 0 && collateralDecrease <= 100) {
        data.push({
          debtIncrease: debtIncrease.toFixed(1),
          collateralDecrease: collateralDecrease.toFixed(2)
        });
      }
    }

    return { ratio, debtOnly, collateralOnly, data };
  }, [inputMode, initialHF, finalHF, initialLTV, finalLTV]);

  const isLiquidatable = inputMode === 'hf' ? finalHF < 1 : finalLTV > (initialLTV * initialHF / 1);

  return (
    <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl shadow-lg">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-800 mb-2 flex items-center gap-2">
          <Activity className="text-blue-600" />
          Loan Liquidation Risk Analyzer
        </h1>
        <p className="text-slate-600">
          Analyze how debt token price increases and collateral token price decreases affect your loan health
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-slate-800">Input Parameters</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Input Mode
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setInputMode('hf')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition ${
                  inputMode === 'hf'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                Health Factor
              </button>
              <button
                onClick={() => setInputMode('ltv')}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition ${
                  inputMode === 'ltv'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                LTV Ratio
              </button>
            </div>
          </div>

          {inputMode === 'hf' ? (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Initial Health Factor: {initialHF.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="3"
                  step="0.1"
                  value={initialHF}
                  onChange={(e) => setInitialHF(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Final Health Factor: {finalHF.toFixed(2)}
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="3"
                  step="0.1"
                  value={finalHF}
                  onChange={(e) => setFinalHF(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </>
          ) : (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Initial LTV: {(initialLTV * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="0.95"
                  step="0.05"
                  value={initialLTV}
                  onChange={(e) => setInitialLTV(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Final LTV: {(finalLTV * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="0.95"
                  step="0.05"
                  value={finalLTV}
                  onChange={(e) => setFinalLTV(parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            </>
          )}

          {isLiquidatable && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={20} />
              <span className="text-sm text-red-800">
                Warning: This position is liquidatable (HF &lt; 1)
              </span>
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4 text-slate-800">Isolated Price Changes</h2>
          
          <div className="space-y-4">
            <div className="p-4 bg-red-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="text-red-600" size={20} />
                <span className="font-semibold text-slate-800">Debt Token Price Increase</span>
              </div>
              <div className="text-3xl font-bold text-red-600">
                +{calculations.debtOnly}%
              </div>
              <p className="text-sm text-slate-600 mt-1">
                (holding collateral price constant)
              </p>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingDown className="text-orange-600" size={20} />
                <span className="font-semibold text-slate-800">Collateral Token Price Decrease</span>
              </div>
              <div className="text-3xl font-bold text-orange-600">
                {calculations.collateralOnly}%
              </div>
              <p className="text-sm text-slate-600 mt-1">
                (holding debt price constant)
              </p>
            </div>

            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-900">
                <strong>Formula:</strong> (1 + α) / (1 + β) = {calculations.ratio.toFixed(4)}
                <br />
                <span className="text-xs">where α = debt price change, β = collateral price change</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <h2 className="text-xl font-semibold mb-4 text-slate-800">
          Combined Price Movement Scenarios
        </h2>
        <p className="text-sm text-slate-600 mb-4">
          This chart shows all combinations of debt price increases (0-100%) and corresponding collateral 
          price decreases (0-100%) that would result in the specified health factor or LTV change.
        </p>
        
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={calculations.data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="debtIncrease" 
              label={{ value: 'Debt Token Price Increase (%)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              label={{ value: 'Collateral Token Price Decrease (%)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              formatter={(value) => `${parseFloat(value).toFixed(2)}%`}
              labelFormatter={(label) => `Debt +${label}%`}
            />
            <Area 
              type="monotone" 
              dataKey="collateralDecrease" 
              stroke="#f97316" 
              fill="#fed7aa" 
              name="Collateral Decrease"
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="p-3 bg-slate-50 rounded">
            <p className="text-xs text-slate-600 mb-1">Starting Point</p>
            <p className="font-semibold">Debt: 0%, Collateral: 0%</p>
          </div>
          <div className="p-3 bg-slate-50 rounded">
            <p className="text-xs text-slate-600 mb-1">Ending Point</p>
            <p className="font-semibold">
              Debt: +{calculations.debtOnly}%, Collateral: {calculations.collateralOnly}%
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-3 text-slate-800">How to Use This Tool</h2>
        <div className="space-y-2 text-sm text-slate-700">
          <p><strong>1. Choose Input Mode:</strong> Select whether you want to work with Health Factor or LTV ratios.</p>
          <p><strong>2. Set Initial and Final Values:</strong> Use the sliders to set your starting and target values.</p>
          <p><strong>3. Interpret Results:</strong></p>
          <ul className="list-disc ml-6 space-y-1">
            <li><strong>Isolated Changes:</strong> Shows how much each token price must change independently</li>
            <li><strong>Combined Scenarios:</strong> The chart shows all valid combinations where both prices move adversely</li>
            <li>Any point on the curve represents a scenario that achieves the target HF/LTV</li>
          </ul>
          <p><strong>4. Risk Assessment:</strong> If final HF &lt; 1, the position becomes liquidatable.</p>
        </div>
      </div>
    </div>
  );
};

export default LoanLiquidationAnalyzer;
```

### Who is this for?

This tool is designed for DeFi users who have:
- **Active lending positions** on protocols like Aave, Compound, or Morpho
- **Collateralized loans** where they need to monitor liquidation risk
- **Portfolio managers** who need to understand price movement impacts on loan health

### User Interaction Flow

**Scenario 1: "How much can prices move before I get liquidated?"**
1. User enters their current Health Factor (e.g., 1.5)
2. Sets the liquidation threshold (HF = 1.0)
3. Tool shows: debt token can increase 50% OR collateral can drop 33.33% before liquidation
4. Chart displays all intermediate scenarios

**Scenario 2: "My LTV increased from 60% to 85%, what happened?"**
1. User switches to LTV mode
2. Enters initial LTV (0.6) and final LTV (0.85)
3. Tool calculates: this is equivalent to debt increasing 41.67% or collateral dropping 29.41%
4. User can see which combination likely occurred

**Scenario 3: "What if both prices move against me?"**
1. User sets current and target HF/LTV
2. Examines the area chart showing all combinations
3. For example: if debt increases 20%, collateral can only drop 18% before liquidation
4. Helps set stop-loss or add-collateral triggers

### Key Formulas Summary

**From Health Factor:**
```
Debt price increase only: α% = [(HF₀/HF₁) - 1] × 100%
Collateral price decrease only: β% = [1 - (HF₁/HF₀)] × 100%
Combined: (1 + α)/(1 + β) = HF₀/HF₁
```

**From LTV:**
```
Debt price increase only: α% = [(LTV₁/LTV₀) - 1] × 100%
Collateral price decrease only: β% = [1 - (LTV₀/LTV₁)] × 100%
Combined: (1 + α)/(1 + β) = LTV₁/LTV₀
```

### Practical Applications

1. **Risk Monitoring:** Set alerts when HF approaches critical thresholds
2. **Position Sizing:** Determine safe leverage levels based on expected volatility
3. **Collateral Management:** Know when to add collateral or reduce debt
4. **Hedging Strategy:** Use the combined scenarios to plan hedges for both tokens
5. **Stress Testing:** Model worst-case scenarios for portfolio risk management

The tool provides both isolated analysis (one price moves) and combined analysis (both prices move), giving you complete visibility into your liquidation risk profile.