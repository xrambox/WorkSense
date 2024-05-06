# WorkSense

### Wellness Tracker
### Overview
The WorkSense Wellness Tracker is a Flask web application designed to track and analyze smoking behavior and stress levels of employees. It utilizes MongoDB for data storage and a logistic regression model for predicting stress levels based on smoking behavior. The detection is based on Deep Learning Model performed on IDS NXD Malibu. 

### Features
User Registration/Login: Users can register and login to access the application.

Real-time Prediction: The application continuously fetches data from a specified API endpoint and updates predictions based on smoking behavior.

Session Management: User sessions are managed securely using Flask session management.

### Installation
Clone the repository:
git clone https://github.com/yourusername/zeiss-wellness-tracker.git

Install dependencies:
pip install -r requirements.txt

Run the Flask application:
python app.py

Access the application in your web browser at http://localhost:1000.

### Usage
Register or login to the application.

View real-time predictions based on smoking behavior.

Logout when done.


### Technologies Used
Python

Flask

MongoDB

scikit-learn

### Credits
This application was developed by Ankit Anand.