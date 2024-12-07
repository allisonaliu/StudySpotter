
# StudySpotter Documentation

## Table of Contents

0. [Demo Video](#demo-video)
1. [Overview](#overview)
2. [Features](#features)
3. [Setup Instructions](#setup-instructions)
4. [Usage](#usage)
5. [Technical Details](#technical-details)
6. [Future Improvements](#future-improvements)

---

## Demo Video

Here is the link to my three-minute demo video on YouTube:
https://youtu.be/-wBlQQBx7kg

---

## Overview

**StudySpotter** is a Flask web application designed to help Harvard College students discover the best places to study on and around campus.

The app determines which study spots to recommend by quizzing users on their unique, highly individual study preferences: ideal environmental noise level, amount of social interaction, level of crowding, size of the space, and level of decoration. StudySpotter then calculates a personalized fit value for every study spot in the database, generating a ranked list of spots for the user to browse at their leisure. If the user is feeling adventurous and wants to discover spots that don't necessarily align with their indicated preferences, they can view a random study spot from the database.

The user can learn more about any study spot by viewing its dynamically generated profile page containing a detailed description of the space, logistical information like hours and address, and an attractive photo. Once a user visits a study spot, they can add a star rating and a personal note to help them remember what they liked and didn't like about the space.

Users can view their own profiles to see the number of spots that they've rated, what their average star rating is, and the numerical study preference values that StudySpotter recorded for them. StudySpotter also enables users to change their account passwords if desired.

This application is built with Python, Flask, SQLite, HTML, CSS (+Bootstrap), and JavaScript for an intuitive user experience.

---

## Features

- **Personalized Quiz:** Quiz to determine each user's personal study preferences.
- **Spot Recommendations:** Ranks study spots in an attractive, accessible format based on user preferences.
- **Random Spots:** Enables adventurous users to discover study spots at random.
- **Spot Profiles:** Renders a detailed profile page for each study spot.
- **User Ratings:** Enables users to rate spots and leave personal notes to reember what they liked and didn't like.
- **Secure User Authentication:** Account creation with hashed passwords to ensure security.

---

## Setup Instructions

To set up and run StudySpotter locally, follow these steps:

### Prerequisites
- Python 3.10 or higher
- Pip

### Installation Steps

Note that CS50 course staff can run this web application on cs50.dev using the files I submitted on Gradescope. The process I outlined below describes how others might access this project. I spent hours trying to use free versions of PythonAnywhere and Vercel to host the application outside of CS50's environment, but I didn't have enough knowledge or experience to resolve the persistent errors I encountered. As a workaround, I created a publicly accessible GitHub repository from which users can clone the application's files.

1. **Clone the GitHub Repository**:
   ```bash
   git clone https://github.com/allisonaliu/studyspotter.git
   cd studyspotter
   ```

2. **Install Dependencies**:
   Use the provided dependencies list `requirements.txt` to install necessary packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   Start the Flask server:
   ```bash
   flask run
   ```

---

## Usage

### Logging In
- Navigate to the login page (displayed by default) to log in, or navigate to the registration page to create a new account.

### Taking the Quiz
- After logging in, navigate to the quiz to set your study preferences.

### Browsing Recommendations
- After taking the quiz, you will be redirected to a list of spots ranked by compatibility with your preferences. Selecting any one of these spots will display its detailed profile page, where you can leave a rating and a note. You can select the Random route from the navbar to view a random study spot's profile page.

### User Profile and Account
- Using the navbar, you can access your profile and account pages to view your stats and change your account password.

---

## Technical Details

- **Framework:** Flask
- **Database:** SQLite
- **Dependencies:** Dependencies are listed in `requirements.txt`.
- **Security Measures:**
  - Secure password storage using `generate_password_hash` and `check_password_hash`.
  - Parameterized queries to prevent SQL injection.

---

## Potential Future Directions

1. **Search Filters:** Allow users to filter spots by specific attributes (e.g. noise level).
2. **Interactive Map:** Add a map to display spots geographically, possibly using Google Maps API.
3. **Public Spot Ratings**: Make ratings and notes public. These features are currently only intended to help users track their personal experiences with spots, but they could be turned into a public review system.
4. **Link Email to Account**: Allow users to link an email address to their account, enabling account recovery, password resetting, and easier communication with users.

---

If you encounter any issues or have any questions, please feel free to send me an email. (Since this document is public on GitHub, I'm not specifying my address here—course staff should have access to it.)

Thank you for using StudySpotter!

