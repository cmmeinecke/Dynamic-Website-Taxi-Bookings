# Triad Taxi Booking website by Group 2 CST 499

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

#Set background image for the website
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
    st.title("Triad Taxi Booking")
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
			
#confirmation email function
def send_confirmation_email(user_email, username, booking_id, pickup_address, dropoff_address, pickup_time, dropoff_time):
    template_id = "d-c600374c10b24f72b9c3af31a60b737d"
    #SendGrid uses this information to pull from the user's booking for the email
    dynamic_data = {
        "booking_id": booking_id,
        "pickup_address": pickup_address,
        "dropoff_address": dropoff_address,
        "pickup_time": pickup_time,
        "dropoff_time": dropoff_time,
        "username": username  
    }

    try:
        message = Mail(
            from_email='cmeinecke@aggies.ncat.edu',
            to_emails=user_email
        )
        message.template_id = template_id
        message.dynamic_template_data = dynamic_data
        #assigns the personal API for the website via SendGrid
        sg = SendGridAPIClient('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')
        sg.send(message)
     #handles email errors
    except Exception as e:
        st.error(f"An error occurred while sending the email: {e}")
			
# Book taxi page and input values into the database
def book_taxi():
    header("Book Taxi")
    email = st.text_input("Email Address (for booking confirmation)")
    pickup_time = st.text_input("Pickup Time (Format 00:00:00)")
    pickup_address = st.text_input("Pickup Address")
    pickup_city = st.text_input("Pickup City")
    pickup_zip = st.text_input("Pickup ZIP Code")
    pickup_country = st.text_input("Pickup Country")
    dropoff_time = st.text_input("Drop-off Time (Format 00:00:00)")
    dropoff_address = st.text_input("Drop-off Address")
    dropoff_city = st.text_input("Drop-off City")
    dropoff_zip = st.text_input("Dropoff ZIP Code")
    dropoff_country = st.text_input("Dropoff Country")
    
    if st.button("Book Taxi"):
        user_id = get_logged_in_user_id()
        if user_id:
            # Validate email input
            if not email or "@" not in email:
                st.error("Please enter a valid email address.")
                return
            
            # Fetch the username from the database using the user_id
            cursor.execute("SELECT username FROM Customer WHERE userID = %s", (user_id,))
            username = cursor.fetchone()[0]
            
            # Get a random cab_id from the Cab table
            cursor.execute("SELECT cab_id FROM Cab ORDER BY RAND() LIMIT 1")
            cab_id = cursor.fetchone()[0]
            
            # Generate random values for package_id and travel_type_id
            package_id = random.randint(1, 7)
            travel_type_id = random.randint(1, 3)
            
            # Insert booking data into the database
            insert_trip_query = """
                INSERT INTO Trip (userID, from_date, to_date, booking_created, website_booking, mobile_booking, package_id, travel_type_id) 
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
            
            # Send booking confirmation email to the user
            send_confirmation_email(
                user_email=email,
                username=username,  
                booking_id=booking_id,
                pickup_address=pickup_address,
                dropoff_address=dropoff_address,
                pickup_time=pickup_time,
                dropoff_time=dropoff_time
            )
            #Displays if booking has been confirmed and email is sent succesfully
            st.success("Taxi booked successfully! A confirmation email has been sent.")

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

# Function that links contact us page to sendgrid server so emails can be sent
def send_email(name, email, message):
    try:
        # Construct SendGrid message
        message = Mail(
            from_email='cmeinecke@aggies.ncat.edu',
            to_emails='cmeinecke@aggies.ncat.edu',
            subject='Message from Triad Taxi Booking App',
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
        
# Payments Page
def payments_page():
    # Add a banner for the launch promo
    promo_banner_html = """
    <div style="
        background-color: #4CAF50;
        color: white;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 18px;
    ">
        🎉 Launch Promo: Pay What You Can! Minimum $5 for the first month. 🚖
    </div>
    """
    st.markdown(promo_banner_html, unsafe_allow_html=True)
    
    # Page title
    st.title("Payment Page")

    # User details section
    st.subheader("Enter Payment Details")
    card_number = st.text_input("Card Number", max_chars=16)
    card_expiry = st.text_input("Expiry Date (MM/YY)")
    card_cvv = st.text_input("CVV", type="password", max_chars=3)
    payment_method = st.selectbox("Select Payment Method", ["Credit Card", "PayPal", "Other"])
    amount = st.number_input("Amount to Pay (Pay-What-You-Can Promotion Min $5.00)", min_value=5.0, step=0.01)

    if st.button("Submit Payment"):
        if card_number and card_expiry and card_cvv and amount > 0:
            try:
                # Simulate payment processing
                payment_success = process_payment(card_number, card_expiry, card_cvv, amount)

                if payment_success:
                    st.success("Payment Successful!")
                    record_payment(amount)
                else:
                    st.error("Payment Failed! Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please fill all the fields correctly.")
    
    # PayPal donation section
    st.subheader("Or Donate via PayPal")
    paypal_button_html = """
    <form action="https://www.paypal.com/donate" method="post" target="_top">
        <input type="hidden" name="business" value="J9G6KJ5Q87LEJ" />
        <input type="hidden" name="no_recurring" value="0" />
        <input type="hidden" name="item_name" value="We are students launching our project website! For the 1st month of launch we are offering pay-what-you-can rides (min of $5)." />
        <input type="hidden" name="currency_code" value="USD" />
        <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
        <img alt="" border="0" src="https://www.paypal.com/en_US/i/scr/pixel.gif" width="1" height="1" />
    </form>
    """
    st.markdown(paypal_button_html, unsafe_allow_html=True)


def process_payment(card_number, expiry, cvv, amount):
    # Dummy payment processing logic
    return True  # Always returns successful for simulation
    
# Function to record payment info into database
def record_payment(amount):
    try:
        query = "INSERT INTO Payments (amount, payment_date) VALUES (%s, %s)"
        values = (amount, datetime.now())
        cursor.execute(query, values)
        db_connection.commit()
        st.info("Payment details saved to the database.")
    except Exception as e:
        st.error(f"Failed to record payment: {e}")

# Set background image
st.set_page_config(page_title="Triad Taxi Booking", page_icon=":taxi:", layout="wide")  # Sets the page title and background image here
set_background(r"C:\Users\tmein\Downloads\taxi\background.png")

# Main function to run the app
def main():
    st.sidebar.title("Navigation")
    pages = {"Login / Sign Up": login_signup, "Book Taxi": book_taxi, "Payments": payments_page, "Contact Us": contact_us }
    current_page = st.sidebar.radio("Go to", list(pages.keys()))

    pages[current_page]()

if __name__ == "__main__":
    main()
