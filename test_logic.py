import unittest
import pandas as pd
from logic import analyze

class LogicTests(unittest.TestCase):
    def row(self, **changes):
        d = dict(product='Strawberries',category='Produce',stock_units=50,daily_demand=10,days_to_expiry=2,price_eur=3.5,unit_weight_kg=0.5,donation_eligible=True)
        d.update(changes)
        return analyze(pd.DataFrame([d])).iloc[0]
    def test_surplus(self):
        r=self.row(); self.assertEqual(r.expected_sales,20); self.assertEqual(r.surplus_units,30); self.assertEqual(r.action,'Discount surplus')
    def test_demand_increase(self):
        r=self.row(daily_demand=30); self.assertEqual(r.surplus_units,0); self.assertEqual(r.action,'Normal sale')
    def test_expired(self):
        r=self.row(days_to_expiry=0); self.assertEqual(r.action,'Remove from sale'); self.assertEqual(r.potential_rescued_kg,0)
    def test_donation(self):
        r=self.row(days_to_expiry=1,daily_demand=5); self.assertEqual(r.action,'Donate surplus'); self.assertEqual(r.donated_units,45)
    def test_no_negative_surplus(self):
        r=self.row(stock_units=3); self.assertEqual(r.surplus_units,0)
    def test_negative_stock_rejected(self):
        with self.assertRaises(ValueError): self.row(stock_units=-1)
    def test_no_donation_if_ineligible(self):
        r=self.row(days_to_expiry=1,donation_eligible=False); self.assertEqual(r.action,'Discount surplus')

if __name__=='__main__': unittest.main()
