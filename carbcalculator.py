# Carb & Insulin Calculator
# Personal tool for insulin dosage calculation
# Intended audience: individuals with diabetes (myself)
# Download file, run in terminal. type in "streamlit run carbcalculator.py" to run!

import os
import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Carb & Insulin Calculator", layout="centered")

# Styling 
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0f1117; }

    .title-block {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .title-block h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 0.25rem;
    }
    .title-block p {
        color: #8b8fa8;
        font-size: 0.9rem;
        margin: 0;
    }

    .glucose-card {
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.25rem;
        font-weight: 600;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .glucose-low    { background: rgba(239,68,68,.15); color: #f87171; border: 1px solid #f87171; }
    .glucose-high   { background: rgba(234,179,8,.15); color: #fbbf24; border: 1px solid #fbbf24; }
    .glucose-normal { background: rgba(34,197,94,.15); color: #4ade80; border: 1px solid #4ade80; }


    .result-box {
        background: #1a1d2e;
        border: 1px solid #2e3250;
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .result-box .label { color: #8b8fa8; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    .result-box .units { font-size: 3rem; font-weight: 700; color: #60a5fa; line-height: 1.1; }
    .result-box .food-name { color: #cbd5e1; font-size: 0.9rem; margin-top: 0.3rem; }

    .history-header {
        color: #8b8fa8;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1.5rem 0 0.5rem 0;
    }

    div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }

    .stButton > button {
        background: #3b5bdb;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        width: 100%;
        transition: background 0.2s;
    }
    .stButton > button:hover { background: #4c6ef5; }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "carbsaver.csv"
CSV_COLS = ["Food", "Carbs (g)", "Insulin Units", "Glucose at Dose"]


# Core class 
class InsulinDosage:

    @staticmethod
    def round_insulin(value: float) -> float:
        """Round to nearest 0.05 units (standard insulin pen increment)."""
        return round(value * 20) / 20

    def calculate_insulin(
        self,
        carb: int,
        carb_ratio: int,
        current_glucose: int,
        target_glucose: int,
        correction_factor: int,
    ) -> tuple[int, bool, str]:
        """
        Returns (total_units, correction_needed, note).
        - Hypoglycemia (<70):  dose = 0, treat the low first.
        - High glucose (≥165): carb dose + correction bolus.
        - Normal:              carb dose only.
        """
        if current_glucose < 70:
            return 0.0, False, "low"

        carb_dose = carb / carb_ratio

        if current_glucose >= 165 and correction_factor > 0:
            bolus = (current_glucose - target_glucose) / correction_factor
            bolus = self.round_insulin(bolus)
            total = self.round_insulin(carb_dose + bolus)
            return total, True, "high"

        return self.round_insulin(carb_dose), False, "normal"

    def save_result(self, food: str, carb: int, total: int, glucose: int) -> None:
        """Append meal entry to CSV log."""
        row = pd.DataFrame([{
            "Food": food,
            "Carbs (g)": carb,
            "Insulin Units": total,
            "Glucose at Dose": glucose
        }])
        header = not os.path.exists(CSV_FILE)
        row.to_csv(CSV_FILE, mode="a", header=header, index=False)

    def load_history(self) -> pd.DataFrame | None:
        if os.path.exists(CSV_FILE):
            try:
                return pd.read_csv(CSV_FILE)
            except pd.errors.ParserError:
                return None
        return None



# UI 
st.markdown("""
<div class="title-block">
    <h1> Carb & Insulin Calculator</h1>
    <p>Use this to help you with your insulin dosage!</p>
</div>
""", unsafe_allow_html=True)

dosage = InsulinDosage()

with st.form("dose_form"):
    col1, col2 = st.columns(2)
    with col1:
        food          = st.text_input("Food / Meal", placeholder="e.g. Sushi, Pizza")
        carb          = st.number_input("Carbohydrates (g)", min_value=0.0, step=1.0)
        current_glucose = st.number_input("Current Glucose (mg/dL)", min_value=0.0, step=1.0)
    with col2:
        carb_ratio      = st.number_input("Carb Ratio (g per unit)", min_value=1.0, step=1.0, value=15.0)
        target_glucose  = st.number_input("Target Glucose (mg/dL)", min_value=0.0, step=1.0, value=100.0)
        correction_factor = st.number_input("Correction Factor", min_value=0.0, step=1.0, value=50.0)

    submitted = st.form_submit_button("Calculate Dose")

if submitted:
    # Validate 
    errors = []
    if not food.strip():
        errors.append("Enter a food name.")
    if carb <= 0:
        errors.append("Carbs must be greater than 0.")
    if carb_ratio <= 0:
        errors.append("Carb ratio must be greater than 0.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # Glucose status banner
        if current_glucose > 0 and current_glucose < 70:
            st.markdown('<div class="glucose-card glucose-low">🔴 Low Blood Sugar — Treat the low before dosing.</div>', unsafe_allow_html=True)
        elif current_glucose >= 165:
            st.markdown('<div class="glucose-card glucose-high">🟡 High Blood Sugar — Correction bolus included.</div>', unsafe_allow_html=True)
        elif current_glucose > 0:
            st.markdown('<div class="glucose-card glucose-normal">🟢 Blood Sugar Normal</div>', unsafe_allow_html=True)

        # Calculate 
        total_insulin, correction_needed, note = dosage.calculate_insulin(
            carb, carb_ratio, current_glucose, target_glucose, correction_factor
        )

        # Result display 
        if note == "low":
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Recommended Dose</div>
                <div class="units" style="color:#f87171;">0 units</div>
                <div class="food-name">Treat hypoglycemia first — do not dose for {food}.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-box">
                <div class="label">Recommended Dose for {food}</div>
                <div class="units">{total_insulin:.2f} units</div>
                <div class="food-name">{carb}g carbs · ratio 1:{int(carb_ratio)}{"  +  correction bolus" if correction_needed else ""}</div>
            </div>
            """, unsafe_allow_html=True)
            dosage.save_result(food.strip(), carb, total_insulin, current_glucose)

        # History
        history = dosage.load_history()
        if history is not None:
            st.markdown('<p class="history-header">📋 Meal Log</p>', unsafe_allow_html=True)
            st.dataframe(history[::-1].reset_index(drop=True), use_container_width=True)

            if st.button("🗑 Clear Log"):
                os.remove(CSV_FILE)
                st.rerun()
