from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os
import numpy as np


from helpers import apology, login_required, fit_format

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///studyspotter.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show welcome page"""

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """Give the user a quiz to determine study preferences"""

    if request.method == "GET":

        # Display the quiz form

        return render_template("quiz.html", fit_format=fit_format, noise=db.execute("SELECT noise FROM users WHERE id = ?", session["user_id"])[0]["noise"])

    else:  # Form submitted via POST

        # Try to display the results of the quiz

        # First, check for missing or invalid user input

        axes = {"noise": request.form.get("noise"),
                "sociality": request.form.get("sociality"),
                "crowding": request.form.get("crowding"),
                "size": request.form.get("size"),
                "decoration": request.form.get("decoration"),
                }

        for key in axes:
            if not axes[key]:
                return apology("Missing field")
            axes[key] = float(axes[key])
            if axes[key] < 0 or axes[key] > 1:
                return apology("Invalid field")

        # Update table users with user's stats

        db.execute("UPDATE users SET noise = ?, sociality = ?, crowding = ?, size = ?, decoration = ? WHERE id = ?",
                   axes["noise"], axes["sociality"], axes["crowding"], axes["size"], axes["decoration"], session["user_id"])

        # Calculate fit values for every spot in the database

        spot_rows = db.execute("SELECT id, noise, sociality, crowding, size, decoration FROM spots")

        fit = 0

        for spot_row in spot_rows:
            # For every spot in the database...
            # Calculate the fit value for this user using the secret StudySpotter formula!
            fit = 1 - ((np.abs(spot_row["noise"] - axes["noise"]) + np.abs(spot_row["sociality"] - axes["sociality"]) + np.abs(
                spot_row["crowding"] - axes["crowding"]) + np.abs(spot_row["size"] - axes["size"]) + np.abs(spot_row["decoration"] - axes["decoration"])) / 5)
            # Insert this calculated fit value into the table fits

            # If the row already exists, update it

            if db.execute("SELECT * FROM fits WHERE user_id = ? AND spot_id = ?", session["user_id"], spot_row["id"]):

                db.execute("UPDATE fits SET fit = ? WHERE user_id = ? AND spot_id = ?",
                           fit, session["user_id"], spot_row["id"])

            # If the row doesn't already exist, insert it

            else:

                db.execute("INSERT INTO fits (user_id, spot_id, fit) VALUES (?, ?, ?)",
                           session["user_id"], spot_row["id"], fit)

        # Flash success message and redirect to homepage

        flash("Quiz submitted successfully!", "success")

        return redirect("/spots")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":

        # Display registration form

        return render_template("register.html")

    else:  # Form was submitted via POST

        # Get username and password from registration form,
        # and perform server-side validation of user input

        username = request.form.get("username")
        if not username:
            # User didn't enter a username
            return apology("Missing username")

        password = request.form.get("password")
        if not password:
            # User didn't enter a password
            return apology("Missing password")
        if len(password) < 8:
            # User overrode minlength attribute; password too short
            return apology("Password too short")

        confirmation = request.form.get("confirmation")

        if password != confirmation:
            # Password and confirmaton don't match
            # (Includes case in which user didn't enter a confirmation)
            return apology("Passwords don't match")

        # Try to insert the username and hashed password
        try:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                       username, generate_password_hash(password))
        except ValueError:
            return apology("Username taken")

        # Log the user in

        session["user_id"] = db.execute(
            "SELECT id FROM users WHERE username = ?", username)[0]["id"]

        # Redirect to homepage and flash message
        flash("You have been registered!", "success")
        return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Display user profile"""

    if request.method == "GET":

        # Display user profile

        user_info = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]

        # Calculate the average rating

        # First, count the number of spots the user has rated

        user_info["num_ratings"] = db.execute(
            "SELECT COUNT(stars) FROM fits WHERE user_id = ? AND stars NOT NULL", session["user_id"])[0]["COUNT(stars)"]

        if user_info["num_ratings"] == 0:
            # The user hasn't rated anything yet
            # Set avg_stars = 0, since an average cannot be calculated
            user_info["avg_stars"] = 0
        else:

            user_info["avg_stars"] = "{:.2f}".format(db.execute(
                "SELECT AVG(stars) FROM fits WHERE user_id = ? AND stars NOT NULL", session["user_id"])[0]["AVG(stars)"])

        return render_template("profile.html", user_info=user_info)

    else:

        # POST not implemented yet

        return redirect("/")


@app.route("/account", methods=["GET", "POST"])
def account():
    """Let the user change their password"""

    if request.method == "GET":

        # Display password-change form

        return render_template("account.html", username=db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"])

    else:  # Form was submitted via POST

        # Check for missing inputs
        if not request.form.get("current_password") or not request.form.get("new_password") or not request.form.get("confirmation"):
            return apology("Missing password")

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Check for valid password length
        if len(new_password) < 8:
            return apology("Password too short")

        # Check that new_password matches confirmation
        if new_password != confirmation:
            return apology("New passwords don't match")

        # Check that old password is valid
        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        if not check_password_hash(
            rows[0]["hash"], current_password
        ):
            return apology("Invalid current password")

        # Inputs are all valid, so change the user's password

        db.execute("UPDATE users SET hash = ? WHERE id = ?",
                   generate_password_hash(new_password), session["user_id"])

        flash("Your password has been changed!", "success")
        return redirect("/")


@app.route("/spot", methods=["GET", "POST"])
def spot():
    """Display a spot's profile and allow the user to leave a star rating and a note"""

    if request.method == "GET":

        # Display this particular spot's detailed profile

        return render_template("spot.html", spot_info=session["spot_info"])

    else:

        # Update this spot's star rating and note based on form fields

        # First, check for missing or invalid user input

        stars = request.form.get("stars")
        note = request.form.get("note")

        if not stars:
            return apology("Missing rating")
        # However, the note variable is allowed to be NULL / None

        if not stars.isnumeric():
            return apology("Invalid rating")
        stars = int(stars)
        # Confirmed type int, so safe to check numeric value
        if stars < 1 or stars > 5:
            return apology("Invalid rating")

        # Update table fits with user's star rating and note

        db.execute("UPDATE fits SET stars = ?, note = ? WHERE user_id = ? AND spot_id = ?",
                   stars, note, session["user_id"], session["spot_info"]["id"])

        flash("Rating and note submitted successfully!", "success")

        return redirect("/spots")


@app.route("/random", methods=["GET"])
def random():
    """Takes the user to a random spot's profile page"""

    spot_count = db.execute("SELECT COUNT(*) FROM spots")[0]["COUNT(*)"]
    random_id = np.random.randint(1, spot_count + 1)

    # session["spot_info"] = db.execute("SELECT * FROM spots WHERE id = ?", random_id)[0]
    spot_info = db.execute(
        "SELECT name, location, hours, spots.id, description, stars, note FROM spots JOIN fits ON spots.id = fits.spot_id WHERE spot_id = ? and user_id = ?", random_id, session["user_id"])
    if not spot_info:
        flash("Please take the StudySpotter Quiz first!", "warning")
        return redirect("/quiz")

    session["spot_info"] = spot_info[0]

    return redirect("/spot")


@app.route("/spots", methods=["GET", "POST"])
def spots():
    """Display the list of study spots, and redirect to the profile for a chosen spot"""

    if request.method == "GET":

        # Display the table of spots so that the user can select one to examine

        spots = db.execute(
            "SELECT name, spots.id, fit, stars FROM spots JOIN fits ON spots.id = fits.spot_id WHERE user_id = ? ORDER BY fit DESC", session["user_id"])

        return render_template("spots.html", spots=spots, fit_format=fit_format)

    else:

        # Display the selected spot's profile

        # First, check for valid input (the user could fake the spot id via inspect)

        spot_info = db.execute("SELECT name, location, hours, spots.id, description, stars, note FROM spots JOIN fits ON spots.id = fits.spot_id WHERE spot_id = ? AND user_id = ?",
                               request.form.get("spot_id"), session["user_id"])

        if not spot_info:
            return apology("Invalid spot")

        session["spot_info"] = spot_info[0]

        return redirect("/spot")
