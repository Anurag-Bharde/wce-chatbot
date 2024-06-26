from flask import Flask, render_template, request, redirect, url_for,flash, jsonify
import nltk
import numpy as np
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bcrypt import hashpw, checkpw, gensalt
import mysql.connector
from mysql.connector import Error
from uuid import uuid4
import pandas as pd
import speech_recognition as sr
import pyttsx3
import matplotlib.pyplot as plt
from io import BytesIO
import base64
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

GREETING_INPUTS = ('hello', 'hi', 'greetings', 'sup', 'what\'s up', 'hey',)
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
other = []


keyword_lists = {
     'placement_info': placement_info,
    'general_info': general_info,
    'library_info': library_info,
    'credit_system': credit_system,
    'course_content': course_content,
    'fees_info': fees_info,
    'other': other
}

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import linear_kernel

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

        # Update count in freqt_query table
        list_name = ''
        max_matches = 0
        for name, keyword_list in keyword_lists.items():
            matches = sum([1 for keyword in keyword_list if keyword in robo_response])
            if matches > max_matches:
                max_matches = matches
                list_name = name

        try:
            if db.is_connected():
                cursor = db.cursor()

                # Check if the query already exists in freqt_query table
                select_query = "SELECT count FROM freqt_query WHERE query = %s"
                cursor.execute(select_query, (list_name,))
                result = cursor.fetchone()

                if result:
                    # If the query exists, update the count
                    update_query = "UPDATE freqt_query SET count = count + 1 WHERE query = %s"
                    cursor.execute(update_query, (list_name,))
                else:
                    # If the query does not exist, insert a new row
                    insert_query = "INSERT INTO freqt_query (query, count) VALUES (%s, 1)"
                    cursor.execute(insert_query, (list_name,))

                db.commit()
                cursor.close()
        except Error as e:
            print(f"Error updating freqt_query table: {e}")

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
# def response(user_response):
#     robo_response = ''
#     sentence_tokens.append(user_response)
    
#     # Append the user response to the dataset
#     vectorizer = TfidfVectorizer(tokenizer=lem_normalize, stop_words='english')
#     tfidf = vectorizer.fit_transform(sentence_tokens)

#     # Calculate cosine similarity
#     values = cosine_similarity(tfidf[-1], tfidf)
#     idx = values.argsort()[0][-2]
#     flat = values.flatten()
#     flat.sort()
#     req_tfidf = flat[-2]

#     if req_tfidf == 0:
#         robo_response = '{} Sorry, I don\'t understand you. How can I improve?'.format(robo_response)
#     else:
#         robo_response = sentence_tokens[idx] + ' Any other questions or feedback?'
    
#     max_matches = 0
#     list_name = ''
#     for name, keyword_list in keyword_lists.items():
#             matches = sum([1 for keyword in keyword_list if keyword in robo_response])
#             if matches > max_matches:
#                 max_matches = matches
#                 list_name = name
        
#         # Append the list name to ans.txt
#     with open('ans.txt', 'a') as f:
#             f.write(list_name + '\n')
#      # Convert text response to speech
#     global engine_busy
#     if not engine_busy:
#         engine_busy = True
#         try:
#             engine.say(robo_response)
#             engine.runAndWait()
#         except Exception as e:
#             print(f"Error converting text to speech: {e}")
#         finally:
#             engine_busy = False

#     # Remove the user response from sentence_tokens
#     sentence_tokens.pop()  # Remove the last item, which is the user's input

#     return robo_response

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
    
    
@app.route('/faq')
def faq():
    try:
       
        query_time_series = "SELECT query, query_date FROM topquery WHERE query_date IS NOT NULL"

        cursor.execute(query_time_series)

        
        top_queries_time_series = cursor.fetchall()

        
        df_time_series = pd.DataFrame(top_queries_time_series, columns=['query', 'query_date'])

        
        df_time_series = df_time_series.dropna(subset=['query_date'])

       
        df_time_series['query_date'] = pd.to_datetime(df_time_series['query_date']).dt.date

       
        query_counts_time_series = df_time_series.groupby('query_date').size()

        # Plotting the time series graph
        plt.figure(figsize=(10, 6))
        query_counts_time_series.plot(kind='line', marker='o', color='b')
        plt.title('Number of Queries Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Queries')

        # Save the time series graph to a bytes object
        img_time_series = BytesIO()
        plt.savefig(img_time_series, format='png')
        img_time_series.seek(0)
        chart_url_time_series = base64.b64encode(img_time_series.getvalue()).decode()
        img_time_series.close()

        # Query to fetch data for the pie chart
        query_pie_chart = "SELECT count, query FROM freqt_query"

        cursor.execute(query_pie_chart)

        # Fetching query results for the pie chart
        top_queries_pie_chart = cursor.fetchall()

        # Extracting data for the pie chart
        queries_pie_chart = [query[1] for query in top_queries_pie_chart]
        counts_pie_chart = [query[0] for query in top_queries_pie_chart]

        # Creating Pie Chart
        plt.figure(figsize=(8, 6))
        plt.pie(counts_pie_chart, labels=queries_pie_chart, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Top Queries Distribution')

        # Save the pie chart to a bytes object
        img_pie_chart = BytesIO()
        plt.savefig(img_pie_chart, format='png')
        img_pie_chart.seek(0)
        chart_url_pie_chart = base64.b64encode(img_pie_chart.getvalue()).decode()
        img_pie_chart.close()
        topquery_query = "SELECT count(*),query FROM topquery where query is not null group by query order by count(*) desc limit 14 "
        cursor.execute(topquery_query)
        topquery_data = cursor.fetchall()

        # Render the FAQ page with both charts and the top query data
        return render_template('faq.html', chart_time_series=chart_url_time_series, chart_pie_chart=chart_url_pie_chart, topquery_data=topquery_data)

    except Error as e:
        print(f"Error: {e}")




    
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
            insert_query = "INSERT INTO TopQuery (userId, query,query_date) VALUES (%s, %s,CURDATE())"
            cursor.execute(insert_query, (user_id, user_query))
            db.commit()
            cursor.close()
            print("Data inserted into the database")
    except Error as e:
        print(f"Error: {e}")


@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/get_response', methods=['POST'])
def get_response():
    try:
        user_response = None

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

    except Exception as e:
        print(f"Error in get_response: {e}")
        return "An error occurred"

# Create a new route to handle user feedback
@app.route('/feedback', methods=['GET','POST'])
def handle_feedback():
    if request.method == 'POST':
        # Retrieve feedback data from the form
        response = int(request.form.get('response', 0))
        correctness = int(request.form.get('correctness', 0))
        clarity = int(request.form.get('clarity', 0))
        comment = request.form.get('comment', '')
        
    try:
        if db.is_connected():
            cursor = db.cursor()
            insert_query = "INSERT INTO feedbacked (response, correctness, clarity, comment) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (response, correctness, clarity, comment))
            db.commit()
            cursor.close()
            flash('Feedback submitted successfully!', 'success')
        else:
            flash('Failed to submit feedback. Please try again later.', 'error')
    except Exception as e:
        print(f"Error: {e}")
        flash('An error occurred while submitting your feedback. Please try again later.', 'error')

    return redirect('/feedback.html')


if __name__ == "__main__":
    app.run(debug=True)
