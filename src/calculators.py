# calculators.py

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio
import io
import base64

# Function to calculate BMI
def calculate_bmi(weight, height):
    bmi = weight / ((height / 100) ** 2)
    return bmi

# Function to generate BMI graph using Seaborn
def generate_bmi_graph(bmi):
    sns.set(style="whitegrid")
    plt.figure(figsize=(6, 4))
    sns.barplot(x=["BMI"], y=[bmi], palette="viridis")
    plt.title("BMI Value")
    
    # Save plot to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    
    # Convert image to base64
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return f'data:image/png;base64,{graph_url}'

# Function to calculate Protein Intake
def calculate_protein_intake(weight, activity_level):
    if activity_level == 'sedentary':
        protein_intake = weight * 0.8
    elif activity_level == 'moderate':
        protein_intake = weight * 1.0
    else:  # active
        protein_intake = weight * 1.2
    return protein_intake

# Function to generate Protein Intake graph using Plotly
def generate_protein_graph(weight, activity_level):
    protein_intake = calculate_protein_intake(weight, activity_level)
    
    # Creating a simple bar graph
    data = [go.Bar(x=["Protein Intake"], y=[protein_intake])]
    layout = go.Layout(title="Recommended Protein Intake (grams)")
    
    fig = go.Figure(data=data, layout=layout)
    
    # Convert Plotly graph to JSON format
    graph_json = pio.to_json(fig)
    return graph_json

# Function to calculate Calories
def calculate_calories(age, gender, weight, height, activity_level):
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    # Adjusting BMR for activity level
    if activity_level == 'sedentary':
        return bmr * 1.2
    elif activity_level == 'moderate':
        return bmr * 1.55
    else:
        return bmr * 1.725

# Function to generate Calorie Needs graph using Plotly
def generate_calorie_graph(age, gender, weight, height, activity_level):
    calories = calculate_calories(age, gender, weight, height, activity_level)
    
    data = [go.Pie(labels=["Calorie Needs"], values=[calories], hole=.3)]
    layout = go.Layout(title="Calorie Needs Breakdown")
    
    fig = go.Figure(data=data, layout=layout)
    
    # Convert Plotly graph to JSON format
    graph_json = pio.to_json(fig)
    return graph_json
