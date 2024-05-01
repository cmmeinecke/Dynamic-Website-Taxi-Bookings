-- CST 498 Taxi Cancellations Database Group 2

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

-- Create the Care_Cancellation table
CREATE TABLE Car_Cancellation (
    car_cancellationID INT AUTO_INCREMENT PRIMARY KEY,
	trip_id INT,
    cancellation TINYINT(1),
    FOREIGN KEY (trip_id) REFERENCES Trip(trip_id)
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

-- Insert values into cab table
INSERT INTO Cab (cab_id) VALUES (102);
INSERT INTO Cab (cab_id) VALUES (103);
INSERT INTO Cab (cab_id) VALUES (104);
INSERT INTO Cab (cab_id) VALUES (105);

