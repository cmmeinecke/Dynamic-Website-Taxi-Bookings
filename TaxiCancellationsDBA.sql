-- CST 499 Taxi Cancellations Database Group 2

-- Create Database
CREATE DATABASE TaxiCancellations;

-- Add TABLES
USE TaxiCancellations;

-- Create the Customer table
CREATE TABLE Customer (
    userID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

-- Create the Trip table
CREATE TABLE Trip (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    userID INT,
    travel_type_id INT,
    package_id INT,
    booking_created DATE,
    from_date TIME,
    to_date TIME,
    online_booking TINYINT(1),
    website_booking TINYINT(1),
    FOREIGN KEY (userID) REFERENCES Customer(userID)
);

-- Create the Cab table
CREATE TABLE Cab (
    cab_id INT AUTO_INCREMENT PRIMARY KEY,
);

-- Create the Booking table
CREATE TABLE Booking (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    userID INT,
    cab_id INT,
    FOREIGN KEY (cab_id) REFERENCES Cab(cab_id),
	FOREIGN KEY (userID) REFERENCES Customer(userID)
);

-- Create the Location table
CREATE TABLE Location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT,
    to_address VARCHAR(255),
    to_city VARCHAR(100),
    to_zip VARCHAR(20),
    to_country VARCHAR(100),
    from_address VARCHAR(255),
    from_city VARCHAR(100),
    from_zip VARCHAR(20),
    from_country VARCHAR(100),
    FOREIGN KEY (trip_id) REFERENCES Trip(trip_id)
);

-- Create the Payments table
CREATE TABLE Payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    card_number VARCHAR(16),
    expiry_date VARCHAR(5),
    cvv INT,
    amount DECIMAL(10, 2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id)
);

-- Insert values into cab table
INSERT INTO Cab (cab_id) VALUES (102);
INSERT INTO Cab (cab_id) VALUES (103);
INSERT INTO Cab (cab_id) VALUES (104);
INSERT INTO Cab (cab_id) VALUES (105);

