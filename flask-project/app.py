#!/usr/local/bin/python3
# Import the necessary modules

from flask import Flask, render_template, request, redirect, url_for, session, flash
from openWeather import get_weather
from forms import LoginForm, SearchForm
from flask_login import login_user, logout_user, login_required, current_user
from models import db, loginManager, UserModel

# Create a new Flask application instance
app = Flask(__name__)
app.secret_key="secret"

#database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#initialize the database
db.init_app(app)

#initialize the login manager
loginManager.init_app(app)

def addUser(email, password):
    user = UserModel()
    user.setPassword(password)
    user.email=email
    db.session.add(user)
    db.session.commit()

#handler for bad requests
@loginManager.unauthorized_handler
def authHandler():
    form=LoginForm()
    flash('Please login to access this page')
    return render_template('login.html',form=form)

# some setup code because we don't have a registration page or database
@app.before_first_request
def create_table():
    db.create_all()
    user = UserModel.query.filter_by(email = 'user@uw.edu' ).first()
    if user is None:
        addUser("user@uw.edu","password")
    else:
        logout_user()

@app.route('/showWeather', methods=['GET', 'POST'])
@login_required
def showWeather():
    city = session.get('city', 'Tacoma')
    weather_data = get_weather(city=city)
    
    # Extract the relevant data from the weather_data response
    weather_forecast = {
        'city': weather_data['city']['name'],
        'current_temperature': weather_data['list'][0]['main']['temp'],
        'current_icon_url': get_weather_icon_url(weather_data['list'][0]['weather'][0]['icon']),
        'current_description': weather_data['list'][0]['weather'][0]['description'],
        'tomorrow_temperature': weather_data['list'][8]['main']['temp'],
        'tomorrow_icon_url': get_weather_icon_url(weather_data['list'][8]['weather'][0]['icon']),
        'tomorrow_description': weather_data['list'][8]['weather'][0]['description']
    }
    
    return render_template('showWeather.html', weather_forecast=weather_forecast)

def get_weather_icon_url(icon_code: str) -> str:
    """Returns the URL of the weather icon image based on the icon code."""
    return f"http://openweathermap.org/img/w/{icon_code}.png"

@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    print(form.email.data)
    print(form.password.data)
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Please enter a valid email and password')
            return render_template('login.html',form=form)
        user = UserModel.query.filter_by(email = form.email.data ).first()
        if user is None:
            print('User not found')
            flash('Please enter a valid email')
            return render_template('login.html',form=form)
        if not user.checkPassword(form.password.data):
            print('Incorrect password')
            flash('Please enter a valid password')
            return render_template('login.html',form=form)
        login_user(user)
        session['email'] = form.email.data
        session['city'] = 'Seattle'
        return redirect(url_for('showWeather'))
    # This function will be called when someone accesses the root URL
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.pop('email', None)
    session.pop('city', None)
    # This function will be called when someone accesses the root URL
    return redirect(url_for('login'))

# Run the application if this script is being run directly
if __name__ == '__main__':
    # The host is set to '0.0.0.0' to make the app accessible from any IP address.
    # The default port is 5000.
    app.run(host='0.0.0.0', debug='true', port=5000)
