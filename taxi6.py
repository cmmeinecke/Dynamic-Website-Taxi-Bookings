# Taxi Cancellations website by Group 2 CST 498

import streamlit as st
import base64
import mysql.connector
from datetime import datetime
import random
import smtplib
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Connect to MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root1",
    database="TaxiCancellations",
    port="3308"
)
cursor = db_connection.cursor()

# Function to execute SQL queries
def execute_query(query, values=None):
    try:
        cursor.execute(query, values)
        db_connection.commit()
        return cursor
    except Exception as e:
        st.error(f"Error executing query: {e}")
        db_connection.rollback()

# Define global variables to store user data
registered_users = {}  # Make registered_users a global variable

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# header function
def header(page_title):
    st.title("Taxi Cancellations")
    st.write("---")
    st.title(page_title)

# Login and sign-up page
def login_signup():
    header("Login / Sign Up")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    action = st.radio("Action", ["Login", "Sign Up"])

    if action == "Login":
        if st.button("Login"):
            # Query the database to check if the username and password match
            query = "SELECT userID FROM Customer WHERE username = %s AND password = %s"
            values = (username, password)
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            if result:
                st.success(f"Welcome back, {username}!")
                # Store user ID in session_state
                st.session_state.user_id = result[0]
                return True
            else:
                st.error("Invalid username or password. Please try again.")
                return False
    else:  # Sign Up
        if st.button("Sign Up"):
            # Insert the new user into the database
            query = "INSERT INTO Customer (username, password) VALUES (%s, %s)"
            values = (username, password)
            cursor.execute(query, values)
            db_connection.commit()
            st.success(f"Account created for {username}! You can now log in.")

            # Clear the input fields after signing up
            st.session_state.username = ""
            st.session_state.password = ""
# book taxi page and input values into the database
def book_taxi():
    header("Book Taxi")
    pickup_time = st.text_input("Pickup Time (Format 00:00:00)")
    pickup_address = st.text_input("Pickup Address")
    pickup_city = st.text_input("Pickup City")
    pickup_zip = st.text_input("Pickup ZIP Code")
    pickup_country = st.text_input("Pickup Country")
    dropoff_time = st.text_input("Drop-off Time (Format 00:00:00)")
    dropoff_address = st.text_input("Drop-off Address")
    dropoff_city = st.text_input("Drop-off City")
    dropoff_zip = st.text_input("Drop-off ZIP Code")
    dropoff_country = st.text_input("Drop-off Country")
    
    if st.button("Book Taxi"):
        user_id = get_logged_in_user_id()
        if user_id:
            # Get a random cab_id from the Cab table
            cursor.execute("SELECT cab_id FROM Cab ORDER BY RAND() LIMIT 1")
            cab_id = cursor.fetchone()[0]
            
            # Generate random values for package_id and travel_type_id
            package_id = random.randint(1, 7)
            travel_type_id = random.randint(1, 3)
            
            # Insert booking data into database
            insert_trip_query = """
                INSERT INTO Trip (userID, from_date, to_date, booking_created, website_booking, online_booking, package_id, travel_type_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            trip_values = (user_id, pickup_time, dropoff_time, datetime.now(), 1, 0, package_id, travel_type_id)
            cursor.execute(insert_trip_query, trip_values)
            db_connection.commit()
            
            # Get the last inserted trip ID
            trip_id = cursor.lastrowid
            
            # Insert pickup and dropoff location data into Location table
            insert_location_query = """
                INSERT INTO Location (trip_id, from_address, from_city, from_zip, from_country, to_address, to_city, to_zip, to_country)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            location_values = (trip_id, pickup_address, pickup_city, pickup_zip, pickup_country,
                               dropoff_address, dropoff_city, dropoff_zip, dropoff_country)
            cursor.execute(insert_location_query, location_values)
            db_connection.commit()
            
            # Generate a random booking_id
            booking_id = random.randint(1000, 9999)
            # Insert booking data into Booking table
            insert_booking_query = "INSERT INTO Booking (booking_id, userID, cab_id) VALUES (%s, %s, %s)"
            booking_values = (booking_id, user_id, cab_id)
            cursor.execute(insert_booking_query, booking_values)
            db_connection.commit()
            
            st.success("Taxi booked successfully!")

# Cancellation likelihood interface
def cancellation_likelihood():
    header("Cancellation Likelihood Prediction")
    # Add code for predicting cancellation likelihood
    likelihood = 0.75  # Example likelihood value
    st.write(f"The likelihood of cancellation is: {likelihood}")

# Contact Us page 
def contact_us():
    header("Contact Us")
    # Add contact information or form for users to contact support
    st.write("Please fill out the form below:")
    name = st.text_input("Name")
    email = st.text_input("Email Address")
    comments = st.text_area("Comments", height=200)
    if st.button("Submit"):
        send_email(name, email, comments)
        st.write("Received! We'll get back to you soon.")

# function that link contact us page to sendgrid server so emails can be sent
def send_email(name, email, message):
    try:
        # Construct SendGrid message
        message = Mail(
            from_email='cmeinecke@aggies.ncat.edu',
            to_emails='cmeinecke@aggies.ncat.edu',
            subject='Message from Streamlit Contact Form',
            html_content=f"<strong>Name:</strong> {name}<br><strong>Email:</strong> {email}<br><br><strong>Message:</strong><br>{message}"
        )
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        st.write("Email sent successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to get the user ID of the currently logged-in user
def get_logged_in_user_id():
    # Check if user_id is already stored in session_state
    if "user_id" in st.session_state:
        return st.session_state.user_id
    else:
        # If not, prompt the user to log in
        st.error("Please log in first.")
        return None

# Set background image
st.set_page_config(page_title="Taxi Cancellations", page_icon=":taxi:", layout="wide")  # Set the page title and background image here
set_background(r"C:\Users\tmein\Downloads\taxi\background.png")

# Main function to run the app
def main():
    st.sidebar.title("Navigation")
    pages = {"Login / Sign Up": login_signup, "Book Taxi": book_taxi, "Cancellation Likelihood": cancellation_likelihood, "Contact Us": contact_us}
    current_page = st.sidebar.radio("Go to", list(pages.keys()))

    pages[current_page]()

if __name__ == "__main__":
    main()
