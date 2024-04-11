import streamlit as st
import base64

# Define global variables to store user data
registered_users = {}
bookings = {}

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

# Common header function
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
            if username in registered_users and registered_users[username] == password:
                st.success(f"Welcome back, {username}!")
                return True
            else:
                st.error("Invalid username or password. Please try again.")
                return False
    else:  # Sign Up
        if st.button("Sign Up"):
            if username in registered_users:
                st.error("Username already exists. Please choose a different username.")
            else:
                registered_users[username] = password
                st.success("Sign up successful. You can now log in.")

# Taxi booking page
def book_taxi():
    header("Book Taxi")
    time = st.text_input("Time")
    pickup_address = st.text_input("Pickup Address")
    dropoff_address = st.text_input("Drop-off Address")
    if st.button("Book Taxi"):
        booking_details = {"Time": time, "Pickup Address": pickup_address, "Drop-off Address": dropoff_address}
        bookings[time] = booking_details
        st.success("Taxi booked successfully!")

# Cancellation likelihood interface
def cancellation_likelihood():
    header("Cancellation Likelihood Prediction")
    # Add code for predicting cancellation likelihood
    likelihood = 0.75  # Example likelihood value
    st.write(f"The likelihood of cancellation is: {likelihood}")

# Contact Us page (formerly Admin Panel)
def contact_us():
    header("Contact Us")
    # Add contact information or form for users to contact support
    st.write("Please fill out the form below:")
    name = st.text_input("Name")
    email = st.text_input("Email Address")
    comments = st.text_area("Comments", height=200)
    if st.button("Submit"):
        st.write("Received! We'll get back to you soon.")

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
