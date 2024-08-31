from flask import Flask, render_template, request, jsonify, session
from config import magic_key, book_text
import os
import google.generativeai as genai
import sqlite3
from datetime import datetime
import uuid
from calculators import calculate_bmi, calculate_protein_intake, calculate_calories, generate_bmi_graph, generate_protein_graph, generate_calorie_graph  # Import calculator and graph functions
import plotly.io as pio

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
app.secret_key = os.urandom(24)  # Secret key for session management

# Configure Google Generative AI
genai.configure(api_key=magic_key)

def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response from Gemini: {e}")
        return "Error generating response."

def build_prompt(book_text, question):
    prompt = f"""
    Given the following book content, answer the question.
    Book Content:
    {book_text}
    Question: {question}
    Answer:
    """
    return prompt

# Database functions
def save_chat(session_id, user_id, message, response):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (session_id TEXT, user_id TEXT, message TEXT, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute("INSERT INTO chats (session_id, user_id, message, response) VALUES (?, ?, ?, ?)",
              (session_id, user_id, message, response))
    conn.commit()
    conn.close()

def get_chat_sessions():
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT session_id FROM chats')
    sessions = [{'session_id': row[0]} for row in c.fetchall()]
    conn.close()
    return sessions

def get_chat_details(session_id):
    conn = sqlite3.connect('chatbot.db')
    c = conn.cursor()
    c.execute('SELECT message, response FROM chats WHERE session_id = ?', (session_id,))
    chats = [{'message': row[0], 'response': row[1]} for row in c.fetchall()]
    conn.close()
    return chats

@app.route('/', methods=['GET'])
def greet():
    # Create a new session ID for each visit
    session['session_id'] = str(uuid.uuid4())
    print("Greet route accessed")
    return render_template('home.html')

@app.route('/guide-bot', methods=['GET'])
def index():
    # Ensure a new session ID is created
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    print("Guide-bot route accessed")
    return render_template('guide_bot.html', session_id=session['session_id'])

@app.route('/get_gemini_answer', methods=['POST'])
def get_gemini_answer():
    user_id = request.remote_addr  # Unique ID for the user (e.g., IP address)
    question = request.json.get('question', '')
    session_id = request.json.get('session_id', session.get('session_id', str(uuid.uuid4())))
    print(f"Question received: {question}")
    prompt = build_prompt(book_text, question)
    gemini_answer = get_gemini_response(prompt)
    save_chat(session_id, user_id, question, gemini_answer)
    return jsonify({'gemini_answer': gemini_answer, 'session_id': session_id})

@app.route('/api/chats', methods=['GET'])
def fetch_chat_sessions():
    sessions = get_chat_sessions()
    return jsonify(sessions)

@app.route('/api/chats/<session_id>', methods=['GET'])
def fetch_chat_details(session_id):
    chats = get_chat_details(session_id)
    return jsonify(chats)

@app.route('/fitness-calculator', methods=['GET'])
def fitness_calculator():
    return render_template('fitness_calculator.html')

@app.route('/fitness_arena', methods=['GET'])
def fitness_arena():
    return render_template('fitness_arena.html')

# Updated paths to match new directory structure
@app.route('/arena/deadlift', methods=['GET'])
def deadlift():
    return render_template('arena/deadlift.html')

@app.route('/arena/bicep_curl', methods=['GET'])
def bicep_curl():
    return render_template('arena/bicep_curl.html')

@app.route('/arena/bench_press', methods=['GET'])
def bench_press():
    return render_template('arena/bench_press.html')

@app.route('/arena/push_ups', methods=['GET'])
def push_ups():
    return render_template('arena/push_ups.html')

@app.route('/arena/squats', methods=['GET'])
def squats():
    return render_template('arena/squats.html')



@app.route('/posture/deadlift_posture', methods=['GET'])
def deadlift_posture():
    return render_template('posture/deadlift_posture.html')

@app.route('/posture/bicep_curl_posture', methods=['GET'])
def bicep_curl_posture():
    return render_template('posture/bicep_curl_posture.html')

@app.route('/posture/bench_press_posture', methods=['GET'])
def bench_press_posture():
    return render_template('posture/bench_press_posture.html')

@app.route('/posture/push_ups_posture', methods=['GET'])
def push_ups_posture():
    return render_template('posture/push_ups_posture.html')

@app.route('/posture/squats_posture', methods=['GET'])
def squats_posture():
    return render_template('posture/squats_posture.html')



@app.route('/posture', methods=['GET'])
def posture():
    return render_template('posture.html')


@app.route('/bmi', methods=['POST'])
def bmi():
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    bmi_result = calculate_bmi(weight, height)
    bmi_graph = generate_bmi_graph(bmi_result)
    return jsonify({'bmi': bmi_result, 'graph': bmi_graph})

@app.route('/protein', methods=['POST'])
def protein():
    weight = float(request.form['weight'])
    activity_level = request.form['activity_level']
    protein_intake = calculate_protein_intake(weight, activity_level)
    protein_graph = generate_protein_graph(weight, activity_level)
    return jsonify({'protein': protein_intake, 'graph': protein_graph})

@app.route('/calories', methods=['POST'])
def calories():
    age = int(request.form['age'])
    gender = request.form['gender']
    weight = float(request.form['weight'])
    height = float(request.form['height'])
    activity_level = request.form['activity_level']
    calories_needed = calculate_calories(age, gender, weight, height, activity_level)
    calorie_graph = generate_calorie_graph(age, gender, weight, height, activity_level)
    return jsonify({'calories': calories_needed, 'graph': calorie_graph})

if __name__ == "__main__":
    app.run(debug=True)
