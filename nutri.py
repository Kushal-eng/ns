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
API_KEY = ("AIzaSyCh6u8pOShzL5Mw8SNDbq7TVjCXd0QPaCo")
if not API_KEY:
    st.error("❌ API Key missing! Please set GEMINI_API_KEY as an environment variable.")
else:
    genai.configure(api_key=API_KEY)

def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # Ensure correct model name
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "⚠️ No response received. Try again."
    except Exception as e:
        return f"⚠️ Error fetching AI response. Please check your API key and model access. ({str(e)})"

st.title("🍽️ AI-Powered Nutrient Deficiency & Health Tracker")

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

# Food intake input
st.write("### 🍏 Enter the food items you consumed today:")
food_input = st.text_area("Type your food items (comma-separated):")

def plot_nutrient_chart(actual_data, recommended_data):
    nutrients = list(actual_data.keys())
    actual_values = list(actual_data.values())
    recommended_values = list(recommended_data.values())
    
    x = np.arange(len(nutrients))
    width = 0.35  # Width of the bars
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width/2, actual_values, width, label='Consumed', color='blue')
    ax.bar(x + width/2, recommended_values, width, label='Recommended', color='green')
    
    ax.set_xlabel("Nutrients")
    ax.set_ylabel("Amount (mg/g) or % of daily intake")
    ax.set_title("Actual vs Recommended Nutrient Intake")
    ax.set_xticks(x)
    ax.set_xticklabels(nutrients)
    ax.legend()
    
    st.pyplot(fig)

if food_input:
    prompt = f"The user consumed {food_input}. Their BMI category is {bmi_category}. Based on this, analyze potential nutrient deficiencies, provide detailed nutrition insights, and recommend food-based improvements."
    
    gemini_output = get_gemini_response(prompt)
    st.write("### 📊 AI-Generated Nutrition Analysis:")
    st.write(gemini_output)
    
    # Additional recommendations
    recommendation_prompt = f"Based on {food_input} and BMI category {bmi_category}, suggest a healthy meal plan for the next day that includes balanced macro and micronutrients."
    meal_plan = get_gemini_response(recommendation_prompt)
    
    st.write("### 🍽️ AI-Generated Meal Plan for Tomorrow:")
    st.write(meal_plan)
    
    # Simulated nutrient data for visualization (replace with actual data extraction from AI response)
    actual_nutrient_data = {"Protein": 50, "Iron": 18, "Calcium": 1000, "Vitamin C": 90, "B12": 2.4}
    recommended_nutrient_data = {"Protein": 60, "Iron": 20, "Calcium": 1200, "Vitamin C": 100, "B12": 2.6}
    
    # Separate section for graphs
    with st.expander("📊 View Nutrient Intake Graphs"):
        plot_nutrient_chart(actual_nutrient_data, recommended_nutrient_data)
    
    # Generate downloadable PDF
    def generate_pdf(content):
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", style='', size=12)
            
            for line in content.split("\n"):
                pdf.cell(200, 10, txt=line.encode("latin-1", "replace").decode("latin-1"), ln=True, align='L')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                pdf.output(temp_file.name, 'F')
                return temp_file.name
        except Exception as e:
            st.error(f"❌ PDF Generation Failed: {str(e)}")
            return None
    
    if st.button("📄 Download Meal Plan as PDF"):
        pdf_content = f"Nutrition Analysis:\n{gemini_output}\n\nMeal Plan for Tomorrow:\n{meal_plan}"
        pdf_path = generate_pdf(pdf_content)
        if pdf_path:
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(label="Download PDF", data=pdf_file, file_name="Meal_Plan.pdf", mime="application/pdf")
else:
    st.info("Please enter food items to analyze your diet.")

st.write("---")
st.write("💡 **Tip:** Try including diverse food groups like grains, proteins, vegetables, and dairy for a balanced diet!")
