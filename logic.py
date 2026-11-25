"""Transparent, illustrative supermarket decision rules; not food safety advice."""
import pandas as pd

REQUIRED = ['product','category','stock_units','daily_demand','days_to_expiry','price_eur','unit_weight_kg','donation_eligible']

def analyze(df: pd.DataFrame, discount_pct: int = 30, demand_lift_pct: int = 50) -> pd.DataFrame:
    if not 0 <= discount_pct <= 90 or not 0 <= demand_lift_pct <= 300:
        raise ValueError('Percentages out of range')
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    out = df.copy()
    for c in ['stock_units','daily_demand','days_to_expiry','price_eur','unit_weight_kg']:
        out[c] = pd.to_numeric(out[c], errors='raise')
    if (out[['stock_units','daily_demand','price_eur','unit_weight_kg']] < 0).any().any():
        raise ValueError('Stock, demand, price and weight cannot be negative')
    if (out['days_to_expiry'] % 1 != 0).any():
        raise ValueError('Days to expiry must be whole numbers')
    out['donation_eligible'] = out['donation_eligible'].astype(str).str.lower().isin(['true','yes','1'])
    out['expected_sales'] = (out.daily_demand * out.days_to_expiry.clip(lower=0)).clip(upper=out.stock_units)
    out['surplus_units'] = (out.stock_units - out.expected_sales).clip(lower=0)
    out['risk'] = out.apply(lambda r: 'Expired' if r.days_to_expiry <= 0 else ('Low' if r.surplus_units == 0 else ('High' if r.days_to_expiry <= 1 else ('Medium' if r.days_to_expiry <= 3 else 'Low'))), axis=1)
    def action(r):
        if r.days_to_expiry <= 0: return 'Remove from sale'
        if r.surplus_units == 0: return 'Normal sale'
        if r.days_to_expiry <= 1 and r.donation_eligible: return 'Donate surplus'
        if r.days_to_expiry <= 3: return 'Discount surplus'
        return 'Normal sale / monitor'
    out['action'] = out.apply(action, axis=1)
    # Scenario assumptions: uplift only affects products recommended for discount.
    out['extra_sales_units'] = out.apply(lambda r: min(r.surplus_units, max(0, r.daily_demand * r.days_to_expiry * demand_lift_pct / 100)) if r.action == 'Discount surplus' else 0, axis=1)
    out['donated_units'] = out.apply(lambda r: r.surplus_units if r.action == 'Donate surplus' else 0, axis=1)
    out['potential_rescued_units'] = out.extra_sales_units + out.donated_units
    out['potential_rescued_kg'] = out.potential_rescued_units * out.unit_weight_kg
    out['baseline_at_risk_kg'] = out.surplus_units * out.unit_weight_kg
    out['estimated_revenue_eur'] = out.extra_sales_units * out.price_eur * (1 - discount_pct / 100)
    out['baseline_value_at_risk_eur'] = out.surplus_units * out.price_eur
    return out
