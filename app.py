import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from datetime import datetime, timezone
from sklearn.linear_model import LogisticRegression
import requests
import time
from flask import render_template



app = Flask(__name__)
app.secret_key = "12345678"  # Replace with a strong secret key

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://user:user@cluster0.pjfqplt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['zeiss']
users_collection = db['zeiss']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if users_collection.find_one({'username': username}):
            flash('Username already exists. Choose a different one.', 'danger')
        else:
            # Initialize the smoking and stress information for employee "Furqan"
            smoking_info_furqan = {'times_smoked_per_day': [3, 4, 5, 3, 4, 3, 5, 5, 5, 3],
                                   'is_stressed_variable': [0, 0, 1, 0, 0, 0, 1, 1, 1, 0]}
            registration_date = datetime.now()

            users_collection.insert_one({'username': username, 'password': password,
                                         'employee': 'Furqan',
                                         'smoking_info': smoking_info_furqan,
                                         'registration_date': registration_date})
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            session['employee'] = user.get('employee', 'Unknown Employee')
            session['smoking_info_employee'] = user.get('smoking_info', {})
            session['registration_date'] = user.get('registration_date')
            flash(f'Login successful for {session["username"]}', 'success')
            
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

def train_logistic_regression(X, y):
    model = LogisticRegression(solver='liblinear', random_state=0)
    model.fit(X, y)
    return model

def make_prediction(model, X):
    return model.predict(X)

def fetch_current_value(api_url, username, password):
    try:
        response = requests.get(api_url, auth=(username, password))
        response.raise_for_status()
        data = response.json()
        current_value = data.get('highlight', {}).get('Highlight', {}).get('value', 'Unknown')
        return current_value
    except Exception as e:
        print("Error occurred:", e)
        return None


smoke_counter = 0
last_increment_time = None

@app.route('/')
def index():
    global smoke_counter, last_increment_time
    if 'username' in session:
        # Fetch smoking information for the logged-in user
        smoking_info = session['smoking_info_employee']
        
        # Prepare data for logistic regression
        X = np.array(smoking_info['times_smoked_per_day']).reshape(-1, 1)
        y = np.array(smoking_info['is_stressed_variable'])
        
        # Train logistic regression model
        model = train_logistic_regression(X, y)
        
        # API endpoint for getting the value
        api_url = "http://169.254.139.11/vapps/classifier/resultsources/last"
        username = "admin"
        password = "sdi"

        # Smoke counter
        

        while True:
            try:
                # Fetch current value
                current_value = fetch_current_value(api_url, username, password)
                
                if "furqansmoke" in current_value:
                    if last_increment_time is None or (datetime.now() - last_increment_time).seconds >= 60:
                        smoke_counter += 1
                        print("here")
                        last_increment_time = datetime.now()
                        print("Smoke counter incremented. New value:", smoke_counter)
                    else:
                        print("Already incremented within 15 minutes (1 minute for demo). Skipping.")
                else:
                    print("Current value is not 'furqansmoke'. Value:", current_value)
                
                print(f"Value changed to: {current_value}. Smoke counter: {smoke_counter}")

                # Make prediction after incrementing smoke_counter
                prediction = make_prediction(model, np.array([[smoke_counter]]))
                print(prediction)
                
                return render_template('index.html', prediction=prediction, smoke_counter=smoke_counter)
                
                time.sleep(5)  # Wait for 5 seconds before checking again
            except KeyboardInterrupt:
                break
                
        
    else:
        flash('You need to login first.', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(port=1000)
