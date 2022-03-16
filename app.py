import pandas as pd
import numpy as np
import plotly.graph_objects as go
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from . import db
from .models import *
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from . import create_app, db
from sqlalchemy.exc import IntegrityError
import plotly.express as px
from datetime import datetime,timedelta


# create app
app = create_app()

# create an application object with the Login Manager class and configure it in your application.

login_manager = LoginManager()
login_manager.init_app(app)


# This function will create database before first API request
@app.before_first_request
def create_table():
    # create database before first request
    db.create_all()
    # create admin before first request
    user = User.query.filter_by(username='admin',email="admin@company.com").first()
    # check if already admin user exist
    if not user:
        user = User(username='admin',email='admin@company.com',phone='54564484984')
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()

# The login_manager provides the user_loader callback, which is responsible for fetching the current user id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# This is the first index route where we are going to
@app.route('/')
def Index():
    return render_template("login.html")

# This route is to register new user
@app.route('/register', methods=['POST'])
def register():
    try:
        if request.method == 'POST':
            # validate required fields
            if not request.form['username'] or not request.form['email'] or not request.form['phone'] or not request.form['phone']:
                flash('Please enter all the fields', 'danger')
            else:
                username = request.form['username']
                email = request.form['email']
                phone = request.form['phone']
                user = User(username, email, phone)
                # set hash generated password
                user.set_password(request.form['password'])

                # save user in database
                db.session.add(user)
                db.session.commit()
                # message to show user
                flash("Registered Successfully", 'success')
    except IntegrityError as e:
        flash("username or email already in use. Kindly use another", 'success')
    return render_template("register.html")

# This route is for login user
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash('Username or Password cannot be empty', 'danger')
        else:
            user = User.query.filter_by(
                username=request.form['username']).first()
            if user is not None and user.check_password(request.form['password']):
                login_user(user)
                next = request.args.get("next")
                return redirect(url_for(next or 'home'))
            flash('Invalid username or Password.', 'danger')
    return render_template('login.html')

# This route is for main home page
@app.route('/home')
@login_required
def home():
     # get login user
    user = load_user(current_user.id)
    trackers = Tracker.query.filter_by(user=user.id).all()
    return render_template('index.html', trackers=trackers, tracker_type=Tracker_type, tracker_values=Tracker_values)


# Flask_login also comes with the logout_user function, which takes care of clearing the current user’s session and logs them out.
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


 # Unauthorized request will be rediected to login page
@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

# ================== User API's ========================

# this route is to get all users
@app.route('/users', methods=['GET'])
@login_required
def users():
    if request.method == 'GET':
        users = User.query.all()
        return render_template('manageUsers.html', users=users)


# This route is for Edit Users using GET and POST methods
@app.route('/edituser/<int:id>', methods=['GET', 'POST'])
@login_required
def EditUser(id):
    try:
        # get user by its Id
        user = User.query.get_or_404(id)
        if request.method == 'POST':
            user.username = request.form['username']
            user.email = request.form['email']
            user.phone = request.form['phone']
            # Update user in database
            db.session.commit()
        else:
            # return json response to client side to fill the Edit User input fields using ajax call in script.js
            return make_response(jsonify(id=user.id, username=user.username, phone=user.phone, email=user.email), 200)
        return redirect(url_for('users'))
    except Exception as e:
        return e

# This route is for deleting User using GET method


@app.route('/deleteuser/<int:id>/', methods=['GET'])
@login_required
def deleteUser(id):
    try:
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        flash("User Deleted Successfully", 'success')
        return redirect(url_for('users'))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('users'))

# ================== Tracker API's ========================


# This route is to get User Trackers using GET method
@app.route('/tracker', methods=['GET'])
@login_required
def tracker():
    try:
        # get login user
        user = load_user(current_user.id)
        trackers = Tracker.query.filter_by(user=user.id).all()
        return render_template('tracker.html', trackers=trackers, tracker_type=Tracker_type, tracker_values=Tracker_values)
    except Exception as e:
        return e

# This route is for Adding Tracker using POST method 
@app.route('/addtracker', methods=['POST'])
@login_required
def Addtracker():
    try:
        # get login user
        user = load_user(current_user.id)
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            tracker_type = request.form['tracker_type']
            tracker_value = request.form['tracker_value']
            options = request.form['options']
            tracker = Tracker(user.id, name, description,
                              tracker_type, tracker_value, options)
            db.session.add(tracker)
            db.session.commit()
        flash('Tracker added successfully !', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('home'))


# This route is for Edit Tracker using POST method
@app.route('/edittracker/<int:id>', methods=['GET', 'POST'])
@login_required
def EditTacker(id):
    try:
        # get user by its Id
        tracker = Tracker.query.get_or_404(id)
        if request.method == 'POST':
            tracker.name = request.form['name']
            tracker.description = request.form['description']
            tracker.tracker_type = request.form['tracker_type']
            tracker.tracker_values = request.form['tracker_value']
            tracker.options = request.form['options']
            # Update user in database
            db.session.commit()
            flash('Tracker Updated Successfully!', 'success')
        else:
            # return json response to client side to fill the Edit User input fields using ajax call in script.js
            return make_response(jsonify(id=tracker.id,
                                         name=tracker.name,
                                         description=tracker.description,
                                         tracker_type=tracker.tracker_type.name,
                                         tracker_value=tracker.tracker_values.name,
                                         options=tracker.options)
                                 , 200)
        return redirect(url_for('home'))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('home'))


# This route is for deleting Tracker using GET method
@app.route('/deletetracker/<int:id>/', methods=['GET'])
@login_required
def deleteTracker(id):
    try:
        tracker = Tracker.query.get_or_404(id)
        db.session.delete(tracker)
        db.session.commit()
        flash("Tracker Deleted Successfully", 'success')
        return redirect(url_for('home'))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('home'))


# ================== Tracker Log API's ========================


# This route is to get User Trackers Logs using GET method
@app.route('/trackerlogs/<int:id>', methods=['GET'])
@login_required
def trackerlogs(id):
    # get login user
    user = load_user(current_user.id)
    tracker = Tracker.query.filter_by(user=user.id,id=id).first()
    try:
        # Data for Chart 
        # Generate chart except for Mutiple Choices
        # converting trackerlogs to dict

        if tracker.tracker_values.name != 2:
            logs = []
            for log in tracker.tracker_logs:
                if log.tracker.tracker_values.value != 2:
                    dictlog = {}
                    dictlog['name'] = log.tracker.name
                    dictlog['value'] = log.value
                    dictlog['timestamp'] = log.timestamp
                    logs.append(dictlog)
            df = pd.DataFrame(logs)
            
            if not df.empty:
                # generate chart using logs dataframe
                fig = generateChart(df)
                # draw chart to html page
                fig.write_html("templates/commons/tracker_chart.html")
            
        return render_template('tracker_logs.html', tracker=tracker)
    except Exception as e:
        flash(e, 'danger')
        return render_template('tracker_logs.html', tracker=tracker)



# draw chart
def generateChart(df):
    # convert timestamp column to df datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # today date
    today = datetime.today()
    # start week date
    start_week = today - timedelta(days=today.weekday())
    # start month date
    start_month = today.replace(day=1)
    
    # today's logs
    dftoday = df[df['timestamp'].dt.strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d')]
    # current week logs
    dfweek = df[(df['timestamp'].dt.strftime('%Y-%m-%d') >= start_week.strftime('%Y-%m-%d') ) & (df['timestamp'].dt.strftime('%Y-%m-%d') <= today.strftime('%Y-%m-%d'))]
    # current month logs
    dfmon = df[(df['timestamp'].dt.strftime('%Y-%m-%d') >= start_month.strftime('%Y-%m-%d') ) & (df['timestamp'].dt.strftime('%Y-%m-%d') <= today.strftime('%Y-%m-%d'))]

    fig = go.Figure()
    # creating dictionary for today, this week, this month
    dfs = {'today':dftoday, 'this week': dfweek, 'this month' :dfmon}
   
    # specify visibility for traces accross dataframes
    frames = len(dfs) # number of dataframes organized in  dict
    columns = len(dfs['today'].columns) - 1 # number of columns i df, minus 1 for Date
    scenarios = [list(s) for s in [e==1 for e in np.eye(frames)]]
    visibility = [list(np.repeat(e, columns)) for e in scenarios] 

    # container for buttons
    buttons = []

    # iterate of dataframes in dfs:
    # - i is used to reference visibility attributes
    # - k is the name for each dataframe
    # - v is the dataframe itself
    for i, (k, v) in enumerate(dfs.items()):
        for c, column in enumerate(v.columns[1:]):
            fig.add_scatter(name = column,
                            x = v['timestamp'],
                            y = v['value'], 
                            visible=True if k=='today' else False # 'daily' values are shown from the start
                        )
                    
        # one button per dataframe to trigger the visibility
        # of all columns / traces for each dataframe
        button =  dict(label=k,
                    method = 'restyle',
                    args = ['visible',visibility[i]])
        buttons.append(button)

    # include dropdown updatemenu in layout
    fig.update_layout(updatemenus=[dict(type="dropdown",
                                        direction="down",
                                        buttons = buttons)])
    return fig
    
# This route is for adding Tracker Logs using POST method
@app.route('/addtrackerlog', methods=['POST'])
@login_required
def AddtrackerLogs():
    try:
        if request.method == 'POST':
            tracker_id = request.form['tracker_id']
            tracker = Tracker.query.get(tracker_id)
            
            # if tracker value is multiple choice
            if tracker.tracker_values.value == 2:
                value = request.form['mcq_value']
            else:
                value = request.form['value']
                
            notes = request.form['notes']
            tracker_logs = Tracker_logs(tracker_id, notes, value)
            db.session.add(tracker_logs)
            db.session.commit()
        flash('Tracker Logs added successfully !', 'success')
        return redirect(url_for('trackerlogs',id=tracker_id))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('trackerlogs',id=tracker_id))
    



# This route is for Edit Tracker Log using GET and POST methods
@app.route('/edittrackerlog/<int:id>', methods=['GET', 'POST'])
@login_required
def EditTackerLog(id):
    try:
        # get Tracker logs by its Id
        tracker_logs = Tracker_logs.query.get_or_404(id)
        if request.method == 'POST':
            tracker_logs.tracker_id = request.form['tracker_id']
            tracker_logs.notes = request.form['notes']
            tracker_logs.value = request.form['value']
            # Update user in database
            db.session.commit()
            flash('Tracker Logs Updated Successfully!', 'success')
        else:
            # return json response to client side to fill the Edit User input fields using ajax call in script.js
            return make_response(jsonify(id=tracker_logs.id,
                                         tracker_id=tracker_logs.tracker_id,
                                         tracker_value=tracker_logs.tracker.tracker_values.value,
                                         notes=tracker_logs.notes, options=tracker_logs.tracker.options,
                                         value=tracker_logs.value)
                                 , 200)
        return redirect(url_for('trackerlogs',id=tracker_logs.tracker_id))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('trackerlogs',id=tracker_logs.tracker_id))


# This route is for deleting Tracker Log using GET method
@app.route('/deletetrackerlog/<int:id>/', methods=['GET'])
@login_required
def deleteTrackerLog(id):
    try:
        tracker_log = Tracker_logs.query.get_or_404(id)
        db.session.delete(tracker_log)
        db.session.commit()
        flash("Tracker Log Deleted Successfully", 'success')
        return redirect(url_for('trackerlogs',id=tracker_log.tracker_id))
    except Exception as e:
        flash(e, 'danger')
        return redirect(url_for('trackerlogs',id=tracker_log.tracker_id))


if __name__ == "__main__":
    app.run(debug=True)
