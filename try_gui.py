from tkinter import *
import requests
import time
import threading
from pymongo import MongoClient
from datetime import datetime
from sklearn.linear_model import LogisticRegression
import numpy as np

# MongoDB setup
uri = "mongodb+srv://user:user@cluster0.pjfqplt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client['zeiss']
users_collection = db['zeiss']

# Function to fetch current value from API
def fetch_current_value():
    try:
        response = requests.get(api_url, auth=(username, password))
        response.raise_for_status()
        data = response.json()
        return data.get('highlight', {}).get('Highlight', {}).get('value', 'Unknown')
    except Exception as e:
        print("Error occurred:", e)
        return None

# Function to update smoke counter
def update_smoke_counter():
    global smoke_counter
    current_value = fetch_current_value()
    if current_value == "furqansmoke":
        smoke_counter += 1
        print("Smoke counter incremented. New value:", smoke_counter)
    else:
        print("Current value is not 'furqansmoke'. Value:", current_value)

# Function to make prediction
def make_prediction():
    global smoke_counter
    prediction = "alert, furqan might be under stress!" if smoke_counter >= 3 else "furqan seems fine."
    return prediction

# Function to update prediction message
def update_prediction():
    prediction = make_prediction()
    prediction_label.config(text=prediction)

# Function to update UI
def update_ui():
    while True:
        update_smoke_counter()
        update_prediction()
        time.sleep(5)  # Wait for 5 seconds before checking again

# Function to register user
def register_user():
    global username_entry, password_entry
    username = username_entry.get()
    password = password_entry.get()
    if users_collection.find_one({'username': username}):
        messagebox.showerror("Error", "Username already exists. Choose a different one.")
    else:
        # Initialize the smoking and stress information for employee "Furqan"
        smoking_info_furqan = {'times_smoked_per_day': [3, 4, 5, 3, 4, 3, 5, 5, 5, 3],
                               'is_stressed_variable': [0, 0, 1, 0, 0, 0, 1, 1, 1, 0]}
        registration_date = datetime.now()

        users_collection.insert_one({'username': username, 'password': password,
                                     'employee': 'Furqan',
                                     'smoking_info': smoking_info_furqan,
                                     'registration_date': registration_date})
        messagebox.showinfo("Success", "Registration successful. You can now log in.")

# Function to login user
def login_user():
    global username_entry, password_entry
    username = username_entry.get()
    password = password_entry.get()
    user = users_collection.find_one({'username': username, 'password': password})
    if user:
        messagebox.showinfo("Success", f'Login successful for {username}')
    else:
        messagebox.showerror("Error", "Invalid username or password. Please try again.")

# Function to logout user
def logout_user():
    messagebox.showinfo("Success", "You have been logged out.")

# API credentials
api_url = "http://169.254.139.11/vapps/classifier/resultsources/last"
username = "admin"
password = "sdi"

# Global variables
smoke_counter = 0

# Tkinter setup
root = Tk()
root.title("Smoke Predictor")

# UI setup
label = Label(root, text="Smoke Predictor", font=("Arial", 16))
label.pack(pady=10)

prediction_label = Label(root, text="", font=("Arial", 14))
prediction_label.pack(pady=10)

# Username and password entry fields
username_label = Label(root, text="Username:")
username_label.pack(pady=5)
username_entry = Entry(root)
username_entry.pack(pady=5)

password_label = Label(root, text="Password:")
password_label.pack(pady=5)
password_entry = Entry(root, show="*")
password_entry.pack(pady=5)

# Register button
register_button = Button(root, text="Register", command=register_user)
register_button.pack(pady=5)

# Login button
login_button = Button(root, text="Login", command=login_user)
login_button.pack(pady=5)

# Logout button
logout_button = Button(root, text="Logout", command=logout_user)
logout_button.pack(pady=5)

# Start updating UI
update_thread = threading.Thread(target=update_ui)
update_thread.daemon = True
update_thread.start()

# Run the Tkinter event loop
root.mainloop()
