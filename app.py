from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Step 1: Establish a Connection to MongoDB
client = MongoClient('mongodb+srv://shikhachoudhari:Shikha123@cluster0.tiysjav.mongodb.net/?retryWrites=true&w=majority')
db = client['wce_chatbot']  # Replace with your desired database name
collection = db['user_info']  # Replace with your desired collection name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insert', methods=['POST'])
def insert_data():
    name = request.form['name']
    email = request.form['email']
    
    # Step 2: Insert Data into MongoDB
    document = {'name': name, 'email': email}
    result = collection.insert_one(document)

    return f'Data inserted successfully! Document ID: {result.inserted_id}'

if __name__ == '__main__':
    app.run(debug=True, port=8000)
