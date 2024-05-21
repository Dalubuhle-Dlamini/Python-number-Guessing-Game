import random
from flask import Flask, url_for, redirect, render_template, request, session, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import base64

lowestNumber = 0
highestNumberLow = 99
highestNumberModerate = 999
highestNumberExpert = 9999
app = Flask(__name__)
app.secret_key = 'Eproject'
app.permanent_session_lifetime = timedelta(hours=1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False


# instances
db = SQLAlchemy(app)

# user model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    # image data start
    img = db.Column(db.BLOB, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    # image data end
    acctype = db.Column(db.String(255), default='user')
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    games_score = db.Column(db.Integer, default=0)
    highest_score = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=100)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<Users: username={self.username}, email={self.email}, acctype={self.acctype}>'

# feedback table model
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Users: username={self.username}, subject={self.subject}, sent={self.sent_at}>'


# routes
@app.route('/')
def index():
    # this will check if session is available
    if 'user' in session:
        name = session["user"]
        # this will filter by name in session
        user = Users.query.filter_by(username=name).first()
        # image conversion
        image = base64.b64encode(user.img).decode("ascii")
        # return page with image
        return render_template('index.html', image=image)
    else:
        # if session is not found then it will return just the page without image
        return render_template('index.html')

# ADMIN ROUTE START
@app.route('/admin')
def admin():
    # will check is user is actually admin
    if 'admin' in session:
        users = db.session.query(Users).all()
        feedback = db.session.query(Feedback).all()
        total = db.session.query(func.sum(Users.games_played)).scalar()
        return render_template('/admin/admin.html', users=users, feedback=feedback, total=total)
    else:
        return redirect(url_for('index'))

@app.route('/admin-users')
def adminUsers():
    if 'admin' in session:
        users = db.session.query(Users).all()
        return render_template('/admin/users.html', users=users)
    else:
        return redirect(url_for('index'))

# route to view feedback from users
@app.route('/admin-feedback')
def adminFeedback():
    if 'admin' in session:
        feedback = db.session.query(Feedback).order_by(Feedback.id.desc())
        return render_template('/admin/notifications.html', feedback=feedback)
    else:
        return redirect(url_for('index'))


@app.route('/add-user', methods=['GET', 'POST'])
def addUser():
    # confirms if the method being used is POST
    if request.method == 'POST':
        # form data collection
        username = request.form['name']
        email = request.form['email']
        image = request.files['image']
        filename = secure_filename(image.filename)
        mimetype = image.mimetype
        password = request.form['password']
        # user is added using constructor
        user = Users(username=username, email=email,
                     img=image.read(), name=filename, mimetype=mimetype)
        # password hash is sent to db
        user.set_password(password)
        # user is added and databse actions are commited
        db.session.add(user)
        db.session.commit()
        # returns the url for viewing users
        return redirect(url_for('adminUsers'))
    # default template to be rendered
    return render_template('/admin/add-user.html')

@app.route("/delete/<int:user_id>")
def delete(user_id):
    # user will be filtered out by id from the url
    user = db.session.query(Users).filter(Users.id == user_id).first()
    # user will be deleted and databse actions are commited
    db.session.delete(user)
    db.session.commit()
    flash('User successfully deleted')
    return redirect(url_for("adminUsers"))

@app.route("/delete-feedback/<int:user_id>")
def deleteFeedback(user_id):
    # user will be filtered out by id from the url
    feedback = db.session.query(Feedback).filter(Feedback.id == user_id).first()
    # user will be deleted and databse actions are commited
    db.session.delete(feedback)
    db.session.commit()
    return redirect(url_for("adminFeedback"))

# update route done by admin
@app.route("/update", methods=["GET", "POST"])
def update():
    if request.method == "POST":
        user_id = request.form["id"]
        # user will be filtered by id from the form
        user = db.session.query(Users).filter(Users.id == user_id).first()
        # form data start
        user.username = request.form["name"]
        user.email = request.form["email"]
        user.acctype = request.form["acctype"]
        user.games_played = int(request.form["played"])
        user.games_won = int(request.form["won"])
        user.games_score = int(request.form["score"])
        user.highest_score = int(request.form["hscore"])
        user.position = int(request.form["position"])
        # form data end
        db.session.commit()
        # if user is successfully updated then this message will be displayed
        flash('User successfully updated')
        return redirect(url_for("adminUsers"))
    else:
        flash('User could not be updated')
# ADMIN ROUTE END


# Register servlet similar to add-user route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['name']
            email = request.form['email']
            image = request.files['image']
            filename = secure_filename(image.filename)
            mimetype = image.mimetype
            password = request.form['password']
            user = Users(username=username, email=email,
                         img=image.read(), name=filename, mimetype=mimetype)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            message = "There is an error user must be registered"
            return render_template('register.html', message=message)
    return render_template('register.html')

# route for editing user profile (performed by user)
# similar to update route
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    name = session['user']
    user = Users.query.filter_by(username=name).first()
    if request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        image = request.files['image']
        filename = secure_filename(image.filename)
        mimetype = image.mimetype
        # for image
        if user:
            # if image data is empty then message will be shown
            if not image:
                message = "no image"
            # if image data is wrong error 400 will be displayed
            elif not filename or not mimetype:
                return 'Bad upload!', 400
            # else image will be added
            else:
                user.img = image.read()
                user.name = filename
                mimetype = mimetype
            user.username = username
            user.email = email
            db.session.commit()
            # this will remove rhe session and redirect user to login page
            if "user" in session:
                session.pop("user", None)
            return redirect(url_for("login"))
    return render_template('edit-profile.html', user=user)

# login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # this will filter user by email
        user = Users.query.filter_by(email=email).first()
        # if user is available
        if user:
            # variables for user details
            acc = user.acctype
            name = user.username
            image = user.img
            # if user details match the ones in database and account type is admin then admin will be redirected to admin page
            if user and user.check_password(password) and acc == 'admin':
                session["user"] = name
                session["admin"] = name
                return redirect(url_for("admin"))
            # if not then user will be redirected to user page
            elif user and user.check_password(password):
                session["user"] = name
                return redirect(url_for("index"))
            # else user will is not available
            else:
                message = 'Invalid username or password'
                return render_template('login.html', message=message, image=image)
        else:
            message = 'Invalid username or password'
            return render_template('login.html', message=message)
    return render_template('login.html')

# contact us route
@app.route("/contact")
def contact():
    if 'user' in session:
        name = session["user"]
        user = Users.query.filter_by(username=name).first()
        image = base64.b64encode(user.img).decode("ascii")
        return render_template('contact.html', image=image)
    else:
        return render_template('contact.html')

# route for viewing user profile
@app.route('/profile')
def profile():
    if 'user' in session:
        name = session["user"]
        user = Users.query.filter_by(username=name).first()
        image = base64.b64encode(user.img).decode("ascii")
        return render_template('profile.html', image=image, user=user)
    else:
        return redirect(url_for('login'))

# feed back similar to add user
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        # if user in session then user id will be added to feedback table
        if 'user' in session:
            name1 = session['user']
            name = request.form["name"]
            number = request.form["number"]
            message = request.form["message"]
            user = Users.query.filter_by(username=name1).first()
            # added to feedback table
            feedback = Feedback(username=name, number=number,
                                message=message, user_id=user.id)
            db.session.add(feedback)
            db.session.commit()
        # else id will not be added
        else:
            name = request.form["name"]
            number = request.form["number"]
            message = request.form["message"]
            feedback = Feedback(username=name, number=number, message=message)
            db.session.add(feedback)
            db.session.commit()
        return redirect(url_for('index'))




# game routes
@app.route('/levels')
def levels():
    if 'user' in session:
        name = session["user"]
        user = Users.query.filter_by(username=name).first()
        image = base64.b64encode(user.img).decode("ascii")
        return render_template('levels.html', image=image)
    else:
        return redirect(url_for('login'))

# leaderboard route
@app.route('/leaderboard')
def leaderboard():
    if 'user' in session:
        name = session["user"]
        user = Users.query.filter_by(username=name).first()
        image = base64.b64encode(user.img).decode("ascii")
        # this will order user by their score and retrieve the top ten leaders
        leaderboard = db.session.query(Users).order_by(
            Users.games_score.desc()).where(Users.position <= 10)
        return render_template('leaderboard.html', image=image, leaderboard=leaderboard)
    else:
        return redirect(url_for('login'))

# game levels
# route for level (low)
@app.route('/gameLow')
def gameLow():
    if 'user' in session:
        # sessions to store info about game
        session['attempt'] = 0
        # session to store number larger than random number
        session['guesses-g'] = 0
        # session to store number smaller than random number
        session['guesses-s'] = 0
        # variable to store random number (0-99) which is stored in session
        low = random.randint(lowestNumber, highestNumberLow)
        session['number'] = low
        return render_template('game.html')
    else:
        return redirect(url_for('login'))

# route for level (moderate)
@app.route('/gameModerate')
def gameModerate():
    if 'user' in session:
        session['attempt'] = 0
        session['guesses-g'] = 0
        session['guesses-s'] = 0
        low = random.randint(lowestNumber, highestNumberModerate)
        session['number'] = low
        return render_template('game-moderate.html')
    else:
        return redirect(url_for('login'))

# route for level (moderate)
@app.route('/gameExpert')
def gameExpert():
    if 'user' in session:
        session['attempt'] = 0
        session['guesses-g'] = 0
        session['guesses-s'] = 0
        low = random.randint(lowestNumber, highestNumberExpert)
        session['number'] = low
        return render_template('game-expert.html')
    else:
        return redirect(url_for('login'))

# routes for game mechanisms
@app.route('/guessLow', methods=['POST'])
def guessLow():
    # maximum attempts a user can have
    maxAttemp = 10
    # current attempts which will be incremented with every attempt
    currentAttempt = 0
    # gets random number stored in form
    low = int(request.form['number'])
    session['guesses'] = []
    # this will run while attempts are less than max attempts
    while session['attempt'] < maxAttemp:
        try:
            # this will store the users guess
            guess = int(request.form['guess'])
            if lowestNumber <= guess <= highestNumberLow:
                if guess < low:
                    # if guess is less than number attempts will increase 
                    session['attempt'] += 1
                    session['guesses-g'] = guess
                    currentAttempt = maxAttemp - session['attempt']
                    # users will be notified how many attempts they hame
                    message = f'Attemps left: {currentAttempt}'
                elif guess > low:
                    # if guess is higher than number attempts will increase
                    session['attempt'] += 1
                    session['guesses-s'] = guess
                    currentAttempt = maxAttemp - session['attempt']
                    message = f'Attemps left: {currentAttempt}'
                elif guess == low:
                    # if number is equal to guess then user wins
                    message = "win"
                else:
                    break
            else:
                # when guess is less than the highest number and greater than lowest number this message will be shown
                message = f"Invalid input please enter a number within specified range {lowestNumber} and {highestNumberLow}."

        except ValueError:
            # if there is a value error the user will get this message
            message = "Invalid input please enter a number."

        if message == "win":
            # number of attempts will be stored here when user wins
            currentAttempt = maxAttemp - (maxAttemp - session['attempt'])
            # user score is calculated
            score = (maxAttemp - session['attempt']) * 5
            name = session['user']
            # user is filtered out from database
            user = Users.query.filter_by(username=name).first()
            if user:
                # user data is updated in the database
                user.games_score = (user.games_score + score)
                user.games_won = (user.games_won + 1)
                user.games_played = (user.games_played + 1)
                if user.highest_score < score:
                    user.highest_score = score

                # positions are updated in the database
                pos = Users.query.order_by(Users.games_score.desc())
                # sorted by score
                for index, player in enumerate(pos):
                    # will update position when position is not equal to index of loop
                    if player.position != index + 1:
                        player.position = index + 1
                # changes are commited 
                db.session.commit()
                # user is then redirected to success page
            return render_template('completed.html', attempts=currentAttempt, status="win", score=score)
        elif session['attempt'] >= maxAttemp:
            # if user loses
            name = session['user']
            user = Users.query.filter_by(username=name).first()
            if user:
                # users games played will be updated
                user.games_played = (user.games_played + 1)
                db.session.commit()
            # user will be redirected to loss page
            return render_template('completed.html', number=low, status="lose")
        else:
            return render_template('game.html', attempts=currentAttempt, message=message)

# mechanism similar to above
@app.route('/guessModerate', methods=['POST'])
def guessModerate():
    maxAttemp = 10
    currentAttempt = 0
    moderate = int(request.form['number'])
    session['guesses'] = []
    while session['attempt'] < maxAttemp:
        try:
            guess = int(request.form['guess'])
            if lowestNumber <= guess <= highestNumberModerate:
                if guess < moderate:
                    session['attempt'] += 1
                    session['guesses-g'] = guess
                    currentAttempt = maxAttemp - session['attempt']
                    message = f'Attemps left: {currentAttempt}'
                elif guess > moderate:
                    session['attempt'] += 1
                    session['guesses-s'] = guess
                    currentAttempt = maxAttemp - session['attempt']
                    message = f'Attemps left: {currentAttempt}'
                elif guess == moderate:
                    message = "win"
                else:
                    break
            else:
                message = f"Invalid input please enter a number within specified range {lowestNumber} and {highestNumberLow}."

        except ValueError:
            message = "Invalid input please enter a number."

        if message == "win":
            currentAttempt = maxAttemp - (maxAttemp - session['attempt'])
            score = (maxAttemp - session['attempt']) * 15
            name = session['user']
            user = Users.query.filter_by(username=name).first()
            if user:
                user.games_score = (user.games_score + score)
                user.games_won = (user.games_won + 1)
                user.games_played = (user.games_played + 1)
                if user.highest_score < score:
                    user.highest_score = score
                pos = Users.query.order_by(Users.games_score.desc())
                for index, player in enumerate(pos):
                    if player.position != index + 1:
                        player.position = index + 1
                db.session.commit()
            return render_template('completed.html', attempts=currentAttempt, status="win", score=score)
        elif session['attempt'] >= maxAttemp:
            name = session['user']
            user = Users.query.filter_by(username=name).first()
            if user:
                user.games_played = (user.games_played + 1)
                db.session.commit()
            return render_template('completed.html', number=moderate, status="lose")
        else:
            return render_template('game-moderate.html', attempts=currentAttempt, message=message)


@app.route('/guessExpert', methods=['POST'])
def guessExpert():
    maxAttemp = 10
    currentAttempt = 0
    expert = int(request.form['number'])
    while session['attempt'] < maxAttemp:
        try:
            guess = int(request.form['guess'])
            if lowestNumber <= guess <= highestNumberExpert:
                if guess < expert:
                    session['attempt'] += 1
                    session['guesses-g'] = guess
                    currentAttempt = maxAttemp - session['attempt']
                    message = f'Attemps left: {currentAttempt}'
                elif guess > expert:
                    session['attempt'] += 1
                    session['guesses-s'] = guess
                    currentAttempt = maxAttemp - session['attempt']
                    message = f'Attemps left: {currentAttempt}'
                elif guess == expert:
                    message = "win"
                else:
                    break
            else:
                message = f"Invalid input please enter a number within specified range {lowestNumber} and {highestNumberLow}."

        except ValueError:
            message = "Invalid input please enter a number."

        if message == "win":
            currentAttempt = maxAttemp - (maxAttemp - session['attempt'])
            score = (maxAttemp - session['attempt']) * 30
            name = session['user']
            user = Users.query.filter_by(username=name).first()
            if user:
                user.games_score = (user.games_score + score)
                user.games_won = (user.games_won + 1)
                user.games_played = (user.games_played + 1)
                if user.highest_score < score:
                    user.highest_score = score
                pos = Users.query.order_by(Users.games_score.desc())
                for index, player in enumerate(pos):
                    if player.position != index + 1:
                        player.position = index + 1
                db.session.commit()
            return render_template('completed.html', attempts=currentAttempt, status="win", score=score)
        elif session['attempt'] >= maxAttemp:
            name = session['user']
            user = Users.query.filter_by(username=name).first()
            if user:
                user.games_played = (user.games_played + 1)
                db.session.commit()
            return render_template('completed.html', number=expert, status="lose")
        else:
            return render_template('game-expert.html', attempts=currentAttempt, message=message)

# GAME ROUTES END

# route for logout
@app.route("/logout")
def logout():
    # removal of session if available
    if "user" in session:
        session.pop("user", None)
    if "admin" in session:
        session.pop("admin", None)
    return redirect(url_for('index'))

# error handlers
@app.errorhandler(400)
def bad_upload(e):
    return render_template('400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# running app
if __name__ == '__main__':
    app.app_context().push()
    db.create_all()
    app.run(debug=True)
