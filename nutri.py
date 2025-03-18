import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import tempfile
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Set page configuration
st.set_page_config(page_title="🍽️ AI-Powered Nutrition & Health Tracker", layout="wide")

# Custom Styling with modern UI enhancements
st.markdown("""
    <style>
        .stApp {background: linear-gradient(to right, #ffefba, #ffffff);}
        h1 {color: #E74C3C; text-align: center; font-size: 42px; font-weight: bold;}
        .stTabs {background-color: #ffffff; border-radius: 12px; padding: 15px;}
        .stSidebar {background: #F39C12; color: white; padding: 15px; border-radius: 12px;}
        .stButton>button {background-color: #E74C3C; color: white; font-size: 18px; border-radius: 8px; padding: 10px;}
        .stTextInput>div>div>input {border-radius: 10px; padding: 10px; border: 2px solid #E74C3C;}
        .big-font {font-size:20px !important; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# Configure Gemini API
API_KEY = "AIzaSyCh6u8pOShzL5Mw8SNDbq7TVjCXd0QPaCo"  # ✅ Replace with your actual API key
genai.configure(api_key=API_KEY)

if not API_KEY:
    st.error("❌ API Key missing! Please set GEMINI_API_KEY as an environment variable.")
else:
    genai.configure(api_key=API_KEY)

def get_gemini_response(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Updated model version
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "⚠️ No response received. Try again."
    except Exception as e:
        return f"⚠️ Error fetching AI response. Please check your API key and model access. ({str(e)})"

st.title("🍽️ AI-Powered Nutrition & Health Tracker")

# Tabs for sections like the reference image
tab1, tab2, tab3, tab4= st.tabs(["🍏 Current Nutrients in Your Diet", "📊 Nutrient Intake Graphs", "🤖 Nutrition Chatbot","🧬 Deficiency Checker"])

# Sidebar - BMI Calculator with new styling
st.sidebar.header("⚖️ BMI Calculator")
st.sidebar.markdown("<div class='big-font'>Enter your details below:</div>", unsafe_allow_html=True)
gender = st.sidebar.selectbox("Gender:", ["Male", "Female", "Other"])
age = st.sidebar.number_input("Age:", min_value=1, max_value=120, step=1)
height = st.sidebar.number_input("Height (cm):", min_value=50, max_value=250, step=1)
weight = st.sidebar.number_input("Weight (kg):", min_value=10, max_value=300, step=1)
activity_level = st.sidebar.selectbox("Activity Level:", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Super Active"])

bmi_category = ""
calories_needed = 0
if height and weight:
    bmi = weight / ((height / 100) ** 2)
    st.sidebar.markdown(f"<div class='big-font'>Your BMI: {bmi:.2f}</div>", unsafe_allow_html=True)
    if bmi < 18.5:
        bmi_category = "underweight"
        st.sidebar.warning("⚠️ You are underweight. Consider a balanced diet.")
    elif 18.5 <= bmi < 24.9:
        bmi_category = "normal"
        st.sidebar.success("✅ Your BMI is normal.")
    elif 25 <= bmi < 29.9:
        bmi_category = "overweight"
        st.sidebar.warning("⚠️ You are overweight. Consider a healthy diet plan.")
    else:
        bmi_category = "obese"
        st.sidebar.error("🚨 You are in the obese category. Consult a nutritionist.")
    
    # Calculate daily calorie needs
    if gender == "Male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    
    activity_multiplier = {"Sedentary": 1.2, "Lightly Active": 1.375, "Moderately Active": 1.55, "Very Active": 1.725, "Super Active": 1.9}
    calories_needed = bmr * activity_multiplier[activity_level]
    st.sidebar.markdown(f"### 🔥 Estimated Daily Calorie Needs: {int(calories_needed)} kcal")


# Updated to use `use_container_width` instead of `use_column_width`
uploaded_file = st.file_uploader("📷 Upload Your Meal Image Here", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="📸 Uploaded Food Image", use_container_width=True)
    image = Image.open(uploaded_file)
    
    st.write("### 🤖 AI Food Analysis in Progress...")

    # Correcting the model to `gemini-1.5-pro-latest` (Vision model not available)
    def analyze_food_image(image):
        try:
            model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Use supported model
            response = model.generate_content(["Describe the food items in this image.", image])
            return response.text if response and hasattr(response, 'text') else "⚠️ Unable to analyze image. Try again."
        except Exception as e:
            return f"⚠️ Error processing image: {str(e)}"

    # Call AI for food recognition
    image_analysis = analyze_food_image(image)
    
    st.write("### 📊 AI-Generated Food Analysis:")
    st.write(image_analysis)



# Current Nutrients in Your Diet (Tab 1)
def generate_pdf(content):
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()
        pdf.set_font("Helvetica", style='', size=12)
        
        pdf.cell(200, 10, "AI-Generated Nutrition Report", ln=True, align='C')
        pdf.ln(5)  # Space
        
        # Ensure all content is ASCII-compatible by replacing unsupported characters
        content = content.encode("ascii", "ignore").decode("ascii")
        
        for section in content.split("\n\n"):
            pdf.set_font("Helvetica", 'B', 12)
            pdf.multi_cell(0, 8, section.split("\n")[0], align='L')
            pdf.ln(2)
            pdf.set_font("Helvetica", '', 11)
            pdf.multi_cell(0, 7, "\n".join(section.split("\n")[1:]), align='L')
            pdf.ln(4)
        
        # Footer
        pdf.set_y(-15)
        pdf.set_font("Helvetica", 'I', 10)
        pdf.cell(0, 10, "Generated by Nutrient Deficiency Detection App", align='C')
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            pdf.output(temp_file.name, 'F')
            return temp_file.name
    except Exception as e:
        st.error(f"❌ PDF Generation Failed: {str(e)}")
        return None

with tab1:
    st.write("### 🍏 Enter the food items you consumed today:")
    food_input = st.text_area("Type your food items (comma-separated):")

    if food_input:
        prompt = f"The user consumed {food_input}. Their BMI category is {bmi_category}. Based on this, analyze potential nutrient deficiencies, provide detailed nutrition insights, and recommend food-based improvements."
        gemini_output = get_gemini_response(prompt)
        st.write("### 📊 AI-Generated Nutrition Analysis:")
        st.write(gemini_output)
        
        recommendation_prompt = f"Based on {food_input} and BMI category {bmi_category}, suggest a healthy meal plan for the next day that includes balanced macro and micronutrients."
        meal_plan = get_gemini_response(recommendation_prompt)
        st.write("### 🍽️ AI-Generated Meal Plan for Tomorrow:")
        st.write(meal_plan)
        
        if st.button("📄 Download Meal Plan as PDF"):
            pdf_content = f"Nutrition Analysis:\n{gemini_output}\n\nMeal Plan for Tomorrow:\n{meal_plan}"
            pdf_path = generate_pdf(pdf_content)
            if pdf_path:
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(label="Download PDF", data=pdf_file, file_name="Meal_Plan.pdf", mime="application/pdf")

# Nutrient Intake Graphs (Tab 2)
with tab2:
    st.write("### 📊 Nutrient Intake Comparison Chart")
    
    # User food input
    food_input = st.text_area("Enter the food items you consumed today (comma-separated):")
    
    if food_input:
        # AI Request to calculate nutrient levels
        nutrient_prompt = f"Analyze the nutritional content of the following foods: {food_input}. Provide values for Protein, Iron, Calcium, Vitamin C, and B12."
        nutrient_data = get_gemini_response(nutrient_prompt)
        
        # Dummy structure to parse AI output (needs proper integration based on AI response format)
        user_nutrient_data = {"Protein": 50, "Iron": 18, "Calcium": 1000, "Vitamin C": 90, "B12": 2.4}  # Replace with AI-extracted values
        recommended_nutrient_data = {"Protein": 60, "Iron": 20, "Calcium": 1200, "Vitamin C": 100, "B12": 2.6}
        
        # Plot Graph
        def plot_nutrient_chart(actual_data, recommended_data):
            nutrients = list(actual_data.keys())
            actual_values = list(actual_data.values())
            recommended_values = list(recommended_data.values())
            
            x = np.arange(len(nutrients))
            width = 0.35  # Width of the bars
            
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(x - width/2, actual_values, width, label='Consumed', color='#2E7D32')
            ax.bar(x + width/2, recommended_values, width, label='Recommended', color='#8BC34A')
            
            ax.set_xlabel("Nutrients")
            ax.set_ylabel("Amount (mg/g) or % of daily intake")
            ax.set_title("Actual vs Recommended Nutrient Intake")
            ax.set_xticks(x)
            ax.set_xticklabels(nutrients, rotation=45)
            ax.legend()
            
            st.pyplot(fig)
        
        plot_nutrient_chart(user_nutrient_data, recommended_nutrient_data)
        
    # Nutrition Chatbot (Tab 3)
with tab3:
    st.write("### 🤖 Ask Your Nutrition Questions!")
    user_query = st.text_input("Ask me anything about nutrition:")
    if user_query:
        response = get_gemini_response(user_query)
        st.write(response)
# Deficiency Checker (Tab 4)
with tab4:
    st.markdown("### 🧬 Check for Possible Deficiencies")
    symptoms = st.multiselect("Select Symptoms You're Experiencing:", 
                              ["Fatigue", "Hair Loss", "Muscle Weakness", "Brain Fog", "Brittle Nails", "Frequent Illness", "Dry Skin", "Poor Night Vision"])
    
    if symptoms:
        deficiency_prompt = f"What vitamins or minerals could be lacking if someone has {', '.join(symptoms)}? Suggest natural food sources to fix it."
        deficiency_results = get_gemini_response(deficiency_prompt)
        st.write(deficiency_results)

st.write("---")
st.write("💡 **Tip:** Try including diverse food groups like grains, proteins, vegetables, and dairy for a balanced diet!")
