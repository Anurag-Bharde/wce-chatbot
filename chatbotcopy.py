from flask import Flask, render_template, request, redirect, url_for,flash
import nltk
import numpy as np
import random
import string
import mysql.connector
from mysql.connector import Error
from bcrypt import hashpw, checkpw, gensalt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from uuid import uuid4
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)
app.secret_key = '123'

FILE_PATH = 'All_Info.txt'

f = open(FILE_PATH, 'r', errors='ignore')
raw = f.read()
raw = raw.lower()

nltk.download('punkt')
nltk.download('wordnet')

sentence_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)

[sentence_tokens[:2], word_tokens[:2]]

lemmer = nltk.stem.WordNetLemmatizer()

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def lem_tokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def lem_normalize(text):
    return lem_tokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

GREETING_INPUTS = ('hello', 'hii','hi', 'greetings', 'sup', 'what\'s up', 'hey',)
GREETING_RESPONSES = ['hi', 'hey', 'hi there', 'hello', 'I am glad! You are talking to me']

def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)
        
general_info = ['college', 'located', 'wce']
placement_info = ['placement', 'tpo', 'package']
library_info = ['library', 'book']
credit_system = ['credit', 'system']
course_content = ['course','content']
fees_info = ['fees', 'open', 'obc']

keyword_lists = {
     'placement_info': placement_info,
    'general_info': general_info,
    'library_info': library_info,
    'credit_system': credit_system,
    'course_content': course_content,
    'fees_info': fees_info
}


# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine_busy = True  # Add this variable to track whether the engine is busy

def response(user_response):
    robo_response = ''
    sentence_tokens.append(user_response)
    
    # Append the user response to the dataset
    vectorizer = TfidfVectorizer(tokenizer=lem_normalize, stop_words='english')
    tfidf = vectorizer.fit_transform(sentence_tokens)

    # Calculate cosine similarity
    values = cosine_similarity(tfidf[-1], tfidf)
    idx = values.argsort()[0][-2]
    flat = values.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if req_tfidf == 0:
        robo_response = '{} Sorry, I don\'t understand you. How can I improve?'.format(robo_response)
    else:
        robo_response = sentence_tokens[idx] + ' Any other questions or feedback?'

     # Convert text response to speech
    global engine_busy
    if not engine_busy:
        engine_busy = True
        try:
            engine.say(robo_response)
            engine.runAndWait()
        except Exception as e:
            print(f"Error converting text to speech: {e}")
        finally:
            engine_busy = False

    # Remove the user response from sentence_tokens
    sentence_tokens.pop()  # Remove the last item, which is the user's input

    return robo_response

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Anuraggb',
    database='wce_chatbot',
    port=3306

)
if db.is_connected():
    print("Connected to MySQL database")
else:
    print("Failed to connect to MySQL database")
cursor = db.cursor()
# Define a route for the login page
# Inside your Flask route function
@app.route('/faq')
def faq():
    cursor.execute("SELECT * FROM faq order by count desc ")  # Assuming 'faq_table' is the name of your table
    data = cursor.fetchall()
    return render_template('faq.html', faq_data=data)

@app.route('/hello_world')
def hello_world():
    return render_template('hello_world.html')


@app.route("/feedback_page")
def feedback_page():
    return render_template("feedback_page.html")

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check login credentials here
        username = request.form.get('username')
        password = request.form.get('password')
        
        cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
        user = cursor.fetchone()
        
        if user and checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return redirect(url_for('home'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('index.html')

# Define a route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the username already exists in the database
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            flash('Username already exists. login .', 'error')
            return render_template('index.html')
        
        # Hash the password before storing it
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        
        # Insert user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        db.commit()
        
        return redirect(url_for('home'))
    
    return render_template('signup.html')

def save_feedback(feedback):
    with open('feedback.txt', 'a') as file:
        file.write(feedback + '\n')


def generate_short_user_id():
    return str(uuid4())[:10]  # Generate a shorter user ID, e.g., the first 10 characters of the UUID

def insert_into_database(user_query):
    try:
        if db.is_connected():
            print("Connected to the database")
            cursor = db.cursor()
            user_id = generate_short_user_id()  # Generate a shorter user ID
            insert_query = "INSERT INTO TopQuery (userId, query) VALUES (%s, %s)"
            cursor.execute(insert_query, (user_id, user_query))
            db.commit()
            cursor.close()
            print("Data inserted into the database")
    except Error as e:
        print(f"Error: {e}")
    # finally:
    #     if db.is_connected():
            # db.close()
            # print("Database connection closed")
    

@app.route("/home")
def home():
    return render_template("home.html")
@app.route("/get_response", methods=['POST'])
def get_response():
    user_response = request.form['user_input']
    user_response = user_response.lower()

    # Check if the request contains an audio file
    if 'audio_input' in request.files:
        recognizer = sr.Recognizer()
        audio_file = request.files['audio_input']

            # Handle audio processing (speech-to-text)
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)
                audio_text = recognizer.recognize_google(audio_data)
            user_response = audio_text.lower()
        except sr.UnknownValueError:
            user_response = "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            user_response = f"Error accessing the Google Speech Recognition API: {e}"

        # If no audio input or the processing failed, use text input
        if user_response is None:
            user_response = request.form.get('user_input', '').lower()

        if user_response != 'bye':
            if user_response == 'thanks' or user_response == 'thank you':
                return "You're welcome!"
            else:
                if greeting(user_response) is not None:
                    return greeting(user_response)
                else:
                    insert_into_database(user_response)
                    return response(user_response)
                    sentence_tokens.remove(user_response)
        else:
            return "Bye! Have a great day. Please Provide Feedback"
        
# @app.route('/save_feedback', methods=['POST'])
# def handle_feedback():
#     feedback = request.form['feedback']
#     save_feedback(feedback)
#     return 'success'

@app.route('/save_feedback', methods=['POST'])
def handle_feedback():
    feedback = request.form['feedback']

    try:
        
        if db.is_connected():
            cursor = db.cursor()
            insert_query = "INSERT INTO UserFeedback (feedback) VALUES (%s)"
            cursor.execute(insert_query, (feedback,))
            db.commit()
            cursor.close()
            return 'success'
    except Error as e:
        print(f"Error: {e}")
    finally:
        if db.is_connected():
            db.close()

    return 'Feedback saved successfully'

if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    
    # 
    # 
    # 
    # 
    # credit_system = [ 'credit', 'system']
    # fees_info = [ 'fees','open','obc']
    # keyword_lists = [general_info, placement_info, library_info,course_content,credit_system,fees_info]