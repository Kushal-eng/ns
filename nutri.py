import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt
import numpy as np

# Ensure set_page_config is the first Streamlit command
st.set_page_config(page_title="AI-Powered Nutrition & Health Tracker", layout="wide")

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")  # Secure API key handling

if not API_KEY:
    st.error("❌ API Key missing! Please set GEMINI_API_KEY as an environment variable.")
else:
    genai.configure(api_key=API_KEY)

# Function to get AI-generated response
def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Use the latest model version
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "⚠️ No response received. Try again."
    except Exception as e:
        return f"⚠️ Error fetching AI response. Please check your API key and model access. ({str(e)})"

# Food Nutrient Data (per 100g or per serving)
food_nutrient_data = {
    "roti": {"Protein": 2.5, "Iron": 0.9, "Calcium": 10, "Vitamin C": 0, "B12": 0},
    "dal": {"Protein": 9, "Iron": 3.3, "Calcium": 45, "Vitamin C": 1, "B12": 0},
    "curd": {"Protein": 3.1, "Iron": 0.2, "Calcium": 120, "Vitamin C": 1, "B12": 0.4},
    "chicken": {"Protein": 27, "Iron": 1.3, "Calcium": 15, "Vitamin C": 0, "B12": 0.5},
    "fish": {"Protein": 20, "Iron": 0.9, "Calcium": 12, "Vitamin C": 0, "B12": 1.2},
    "milk": {"Protein": 3.4, "Iron": 0.1, "Calcium": 125, "Vitamin C": 0, "B12": 1.1},
}

# Function to calculate total nutrients from user input
def calculate_nutrient_intake(user_foods):
    total_nutrients = {"Protein": 0, "Iron": 0, "Calcium": 0, "Vitamin C": 0, "B12": 0}
    
    for food in user_foods:
        food = food.strip().lower()
        if food in food_nutrient_data:
            for nutrient, value in food_nutrient_data[food].items():
                total_nutrients[nutrient] += value
    
    return total_nutrients

st.title("🍽️ AI-Powered Nutrition & Health Tracker")

# Tabs for sections like the reference image
tab1, tab2 = st.tabs(["🍏 Current Nutrients in Your Diet", "📊 Nutrient Intake Graphs"])

# Sidebar - BMI Calculator
st.sidebar.header("⚖️ BMI Calculator")
age = st.sidebar.number_input("Enter your age:", min_value=1, max_value=120, step=1)
height = st.sidebar.number_input("Enter your height (cm):", min_value=50, max_value=250, step=1)
weight = st.sidebar.number_input("Enter your weight (kg):", min_value=10, max_value=300, step=1)

bmi_category = ""
if height and weight:
    bmi = weight / ((height / 100) ** 2)
    st.sidebar.write(f"### Your BMI: {bmi:.2f}")
    if bmi < 18.5:
        bmi_category = "underweight"
        st.sidebar.warning("You are underweight. Consider a balanced diet.")
    elif 18.5 <= bmi < 24.9:
        bmi_category = "normal"
        st.sidebar.success("Your BMI is normal.")
    elif 25 <= bmi < 29.9:
        bmi_category = "overweight"
        st.sidebar.warning("You are overweight. Consider a healthy diet plan.")
    else:
        bmi_category = "obese"
        st.sidebar.error("You are in the obese category. Consult a nutritionist.")

# Current Nutrients in Your Diet (Tab 1)
with tab1:
    st.write("### 🍏 Enter the food items you consumed today:")
    food_input = st.text_area("Type your food items (comma-separated):")

    if food_input:
        user_foods = food_input.split(",")
        actual_nutrient_data = calculate_nutrient_intake(user_foods)
        
        prompt = f"The user consumed {food_input}. Their BMI category is {bmi_category}. Based on this, analyze potential nutrient deficiencies, provide detailed nutrition insights, and recommend food-based improvements."
        gemini_output = get_gemini_response(prompt)
        st.write("### 📊 AI-Generated Nutrition Analysis:")
        st.write(gemini_output)
        
        recommendation_prompt = f"Based on {food_input} and BMI category {bmi_category}, suggest a healthy meal plan for the next day that includes balanced macro and micronutrients."
        meal_plan = get_gemini_response(recommendation_prompt)
        st.write("### 🍽️ AI-Generated Meal Plan for Tomorrow:")
        st.write(meal_plan)

# Nutrient Intake Graphs (Tab 2)
with tab2:
    st.write("### 📊 Nutrient Intake Comparison Chart")
    recommended_nutrient_data = {"Protein": 60, "Iron": 20, "Calcium": 1200, "Vitamin C": 100, "B12": 2.6}
    
    def plot_nutrient_chart(actual_data, recommended_data):
        nutrients = list(actual_data.keys())
        actual_values = list(actual_data.values())
        recommended_values = list(recommended_data.values())
        
        x = np.arange(len(nutrients))
        width = 0.35  # Width of bars
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width/2, actual_values, width, label='Consumed', color='blue')
        ax.bar(x + width/2, recommended_values, width, label='Recommended', color='green')
        
        ax.set_xlabel("Nutrients")
        ax.set_ylabel("Amount (mg/g) or % of daily intake")
        ax.set_title("Actual vs Recommended Nutrient Intake")
        ax.set_xticks(x)
        ax.set_xticklabels(nutrients, rotation=45)
        ax.legend()
        
        st.pyplot(fig)
    
    if food_input:
        plot_nutrient_chart(actual_nutrient_data, recommended_nutrient_data)

st.write("---")
st.write("💡 **Tip:** Try including diverse food groups like grains, proteins, vegetables, and dairy for a balanced diet!")
