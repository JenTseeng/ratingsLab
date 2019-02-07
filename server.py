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

@app.route("/movies")
def movies_list():
    """Show list of movies."""
    movies = Movie.query.order_by(Movie.title).all()
    # movies = Movie.query.all()
    return render_template("movie_list.html", movies=movies)

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

    # all_users = db.session.query(User.user_id)
    # user_id = all_users.filter(User.email==email_to_check, User.password==pw).first()
    user = User.query.filter(User.email==email_to_check, User.password==pw).first()

    if user:

        session['user_id'] = user.user_id

        flash("You are now logged in!")

        return redirect("/users/<user.user_id>")

    else:

        flash("Credentials incorrect. Please try again.")

        return redirect("/login") 


@app.route('/logout')
def logout():
    """Logout page"""
    del session['user_id']
    flash("You are now logged out!")

    return redirect("/")


@app.route('/users/<user_id>')
def show_user_details(user_id):
    """User detail page"""
    user = User.query.get(int(user_id))

    return render_template("user_info.html", user=user)


@app.route('/movies/<movie_id>')
def show_movie_details(movie_id):
    """Movie detail page"""
    movie = Movie.query.get(int(movie_id))

    return render_template("movie_info.html", movie=movie)


@app.route('/submit_rating/<movie_id>', methods=["POST"])
def process_rating(movie_id):
    """Enter or update user's rating for a movie"""

    user_r = request.form.get('rating')

    existing_r = Rating.query.filter(Rating.movie_id==movie_id, Rating.user_id==session['user_id']).first()

    if existing_r:
        existing_r.score = user_r
        db.session.commit()

    else:
        new_rating = Rating(movie_id=movie_id,user_id=session['user_id'],score=user_r)
        db.session.add(new_rating)
        db.session.commit()


    return redirect("/")


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
