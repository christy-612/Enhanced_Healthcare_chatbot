from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import google.generativeai as ai

app = Flask(__name__)

# Replace with a secure way to store API keys, such as environment variables, for production use
API_KEY = 'AIzaSyCaaYk79vEPaV262-zR2gENiwMwM0vc_Qw'
ai.configure(api_key=API_KEY)
model = ai.GenerativeModel("gemini-pro")

# Secret key for session management
app.secret_key = 'replace_with_a_different_secret_key'


class AI_Assistant:
    def __init__(self):
        # Initialize AI model with psychiatrist persona
        self.full_transcript = [
            {"role": "system", "content": "You are a compassionate and responsible psychiatrist. Listen attentively, provide supportive responses, and offer guidance in a calm, reassuring tone."},
        ]
        self.chat = model.start_chat()

    def generate_ai_response(self, user_input):
        # Append user message to conversation context
        self.full_transcript.append({"role": "user", "content": user_input})

        # Generate a medium-length response with the Gemini API
        prompt = f"As a psychiatrist, provide a supportive, medium-length response (around 2-3 sentences) to: {user_input}"
        response = self.chat.send_message(prompt)
        ai_response = response.text.strip()

        # Append AI response to conversation context
        self.full_transcript.append({"role": "assistant", "content": ai_response})
        return ai_response


ai_assistant = AI_Assistant()

# Default route for checking login status
@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('chatbot'))
    return redirect(url_for('login'))

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the entered email and password match the ones stored in the session
        if email == session.get('registered_email') and password == session.get('registered_password'):
            session['logged_in'] = True
            return redirect(url_for('chatbot'))
        else:
            return render_template('login.html', error="Incorrect email or password. Please try again.")
    
    return render_template('login.html')

# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Store the email and password in session for this example
        session['registered_email'] = request.form['email']
        session['registered_password'] = request.form['password']
        return redirect(url_for('login'))
    
    return render_template('signup.html')

# Chatbot page, requires login
@app.route('/chat', methods=['GET'])
def chatbot():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('chatbot.html')

# API route for chatbot responses
@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')

    # Provide a response based on user input
    if user_message.lower() == 'bye':
        response_text = "Goodbye! Take care of yourself, and remember, help is always available if you need it."
    else:
        response_text = ai_assistant.generate_ai_response(user_message)
    
    return jsonify({'response': response_text})

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
