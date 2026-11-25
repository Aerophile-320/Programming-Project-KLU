# FoodWise v1.0 — Supermarket Food Waste Rescue Assistant

A beginner-friendly, rule-based Streamlit dashboard for classroom demonstration. All sample data is **synthetic/fictional**.

## Windows setup (VS Code)

1. Extract `FoodWise_v1.zip` using Windows File Explorer: right-click ZIP → **Extract All**.
2. In VS Code, select **File → Open Folder** and choose the extracted `FoodWise_v1` folder (the one containing `app.py`).
3. Open **Terminal → New Terminal**.
4. Run `uv sync` to create a project environment and install required packages.
5. Run `uv run streamlit run app.py` to start the dashboard.
6. Open the local URL shown in the terminal, usually `http://localhost:8501`.
7. Stop the app with **Ctrl+C** in the terminal. Restart with the same `uv run streamlit run app.py` command.

Requires Python 3.13, uv, and VS Code. VS Code Python extension is recommended, not required for launching. First dependency installation needs internet; after installation the demo uses no external API.

## Testing

Run `uv run python -m unittest -v test_logic.py`. The tests cover surplus, demand changes, expiry, donation, negative inputs and eligibility.

## Live demo

1. Find **Strawberries 500g**: stock 50, demand 10/day, 2 days to expiry.
2. Expected sales = 20, surplus = 30, action = Discount surplus.
3. Change daily demand to **30** in the editable table.
4. Expected sales = 50 (capped at stock), surplus = 0, action = Normal sale. Notice the KPI and charts update.
5. Restore daily demand to 10, then try different discount uplift assumptions in the sidebar.

## Model assumptions and limitations

- `days_to_expiry` is a synthetic numeric field; **not** a real food safety assessment.
- Expired products are flagged for removal, not for donation or discounting.
- Risk thresholds and actions are illustrative, not universal retail rules.
- Expected sales = min(stock, daily demand × max(days remaining, 0)).
- Surplus = max(stock − expected sales, 0).
- Discount response is a user-chosen *assumption*, not forecasted demand. Estimated discount revenue is not profit.
- Donations are assumed to be accepted in full for eligible products, which may overstate rescue potential.
- No guarantee of avoided waste, no CO₂ claim, no real supplier or store connection.
- Donation eligibility must be confirmed by trained staff in a real store; follow food safety law and store policies.

## Project files

- `app.py`: Streamlit interface, visualizations and interactions.
- `logic.py`: deterministic analysis and recommendations.
- `sample_data.csv`: fictional inventory.
- `test_logic.py`: automated logic checks.
- `pyproject.toml`: Python dependencies.

**AI reflection:** Record real development successes and mistakes after local installation and testing; do not invent an AI failure.
