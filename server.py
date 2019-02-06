"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)

from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/registration")
def new_user():
    """Shows registration form"""

    return render_template("registration.html")

@app.route("/confirm_registration", methods=['POST'])
def add_user():
    """Add new user."""
    email_to_check = request.form.get('email')
    pw = request.form.get('pw')

    if User.query.filter(User.email==email_to_check).first():
        # do nothing, show message
        flash("User already exists. Please enter a different email or login.")
        return redirect("/registration")

    else:
        user = User(email=email_to_check, password=pw)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)
        db.session.commit()

        # Confirm registration and redirect to homepage
        flash("Successfully registered!")
        return redirect("/")


@app.route('/login')
def login():
    """Login page"""
    return render_template("login.html")


@app.route('/check_login', methods = ["POST"])
def check_login():
    """Check credentials"""

    email_to_check = request.form.get('email')
    pw = request.form.get('pw')

    all_users = db.session.query(User.user_id)
    user_id = all_users.filter(User.email==email_to_check, User.password==pw).first()

    if user_id:

        session['user_id'] = user_id

        flash("You are now logged in!")

        return redirect("/")

    else:

        flash("Credentials incorrect. Please try again.")

        return redirect("/login") 


    # try:
    #     user = User.query.filter(User.email==email_to_check).one()

    # except:
    #     flash("User does not exist. Please try again.")
    #     return redirect("/login")  


    # if user.password == pw:
    #     session['user id'] = user.user_id
    #     flash("You are now logged in!")

    #     return redirect("/")

    # else:
    #     flash(" Please try again.")
    #     return redirect("/login") 




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
