# point of this project is to create a personal carb calculator for diabetes.
# this serves are a carb calculator for those with diabetes.
# intended audience are individuals with diabetes, aka myself.
# when I learn how to design an app I will implement this and see how it runs.
# for now just setting main frame work
import os
import streamlit as st
import pandas as pd

st.sidebar.title("Carb & Insulin Calculator")
food = st.sidebar.text_input("Food")
carb = st.sidebar.number_input("Carbs", min_value=0)
carb_ratio = st.sidebar.number_input("Carbs per Unit of Insulin", min_value=1)
current_glucose = st.sidebar.number_input("Current Glucose", min_value=0)
target_glucose = st.sidebar.number_input("Target Glucose", min_value=0)
correction_factor = st.sidebar.number_input("Correction Factor", min_value=0)


class InsulinDosage:
    
    def calculate_insulin(self,carb,carb_ratio,current_glucose,target_glucose,correction_factor):
        '''
        First asks what they are eating, then the amount of carbs within the meal
        Then asks for personal carbs/unit of insulin dosage, then does the math for them
        
        '''
        insulin = carb/carb_ratio
        
        if current_glucose >= 165 and correction_factor > 0:
            bolus = ((current_glucose - target_glucose)/correction_factor)
            bolus_rounded = round(bolus * 20) / 20
            total = float(insulin + bolus_rounded)
            total = round(total * 20) / 20
            correction_needed = True
        else:
            total = round(insulin * 20) / 20
            correction_needed = False
               
        return total, correction_needed, 
    
    
    def save_results(self, food, carb, total):
        '''
        Saves last eaten meal into a csv file for later.
        '''
        data = {"Food": [food], "Carbs": [carb], "Insulin Units": [total]}
        df = pd.DataFrame(data)
        df.to_csv("carbsaver.csv", mode="w", header=False, index=False)

if food and carb > 0 and carb_ratio > 0:
    dosage = InsulinDosage()
    total_insulin, correction_needed = dosage.calculate_insulin(
        carb, carb_ratio, current_glucose, target_glucose, correction_factor
    )
    if correction_needed:
        st.warning("⚠️ High blood sugar! Correction needed.")
    else:
        st.success("Blood sugar is normal.")
    st.write(f"You will need {total_insulin} units of insulin for your {food}.")
    dosage.save_results(food, carb, total_insulin)
    
    if os.path.exists("carbsaver.csv"):
        history = pd.read_csv("carbsaver.csv", names=["Food", "Carbs", "Insulin Units"])
        st.table(history)

