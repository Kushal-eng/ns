import streamlit as st
import google.generativeai as genai
import pdfkit
import tempfile

genai.configure(api_key="AIzaSyCb0NhBUY35pb_WLqnMrlopnty43y152_s")

def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

st.set_page_config(page_title="AI-Powered Nutrition & Health Tracker", layout="wide")
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

def generate_pdf(content):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdfkit.from_string(content, temp_file.name)
        return temp_file.name

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
    
    # Generate downloadable PDF
    if st.button("📄 Download Meal Plan as PDF"):
        pdf_content = f"Nutrition Analysis:\n{gemini_output}\n\nMeal Plan for Tomorrow:\n{meal_plan}"
        pdf_path = generate_pdf(pdf_content)
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(label="Download PDF", data=pdf_file, file_name="Meal_Plan.pdf", mime="application/pdf")
else:
    st.info("Please enter food items to analyze your diet.")

st.write("---")
st.write("💡 **Tip:** Try including diverse food groups like grains, proteins, vegetables, and dairy for a balanced diet!")
