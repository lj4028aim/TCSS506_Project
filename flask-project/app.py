#!/usr/local/bin/python3
# Import the necessary modules

from flask import Flask, render_template, request, redirect, url_for, session, flash
from openWeather import get_cur_weather, get_weather
from music import retrieve_playlist_data
from forms import LoginForm
from flask_login import login_user, logout_user, login_required
from models import db, loginManager, UserModel
from datetime import datetime, timedelta
import sqlite3

# Create a new Flask application instance
app = Flask(__name__)
app.secret_key="secret"

# database configuration
DBUSER = 'user'
DBPASS = 'password'
DBHOST = 'db'
DBPORT = '5432'
DBNAME = 'pglogindb'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
        user=DBUSER,
        passwd=DBPASS,
        host=DBHOST,
        port=DBPORT,
        db=DBNAME)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
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


@app.route('/')
def showLanding():
    """Show landing page"""
    return render_template('landing.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def showWeather():
    """
    Show the weather forecast for a given city, state, and country."""

    if request.method == 'POST':
        # Get the location from the form
        location = request.form.get('location')
        # Split the location into city, state, and country
        parts = location.split(',')
        num_parts = len(parts)

        if num_parts >= 1:
            city = parts[0].strip()
        # Get the state and country based on the location
        state, country = get_location(city_name=location)

        # Fetch weather data based on the entered city and State
        cur_weather_data = get_cur_weather(city=city, state=state, country=country, units="imperial")
        weather_data = get_weather(city=city, state=state, country=country, units="imperial")
    else:
        cur_weather_data = get_cur_weather(city="Tacoma", state="Washington", country="US", units="imperial")
        weather_data = get_weather(city="Tacoma", state="Washington", country="US", units="imperial")
    
    # Save the weather_data response to a file for debugging purposes
    # with open('weather_data.txt', 'w') as f:
    #     f.write(str(weather_data))

    # with open('cur_weather_data.txt', 'w') as f1:
    #     f1.write(str(cur_weather_data))

    # Extract the list of weather forecasts from the weather_data response
    wforecast = weather_data['list']
    
    # Calculate the number of minutes since the last update
    time_now = datetime.now()
    last_time_updated = datetime.fromtimestamp(cur_weather_data['dt'])
    last_updated = int((time_now - last_time_updated).total_seconds() // 60)

    # Extract current weather data from cur_weather_data response
    weather_forecast = {
        'city': cur_weather_data['name'],
        'state_country': get_location(city_id=cur_weather_data['id']),
        'current_temperature': int(cur_weather_data['main']['temp']),
        'current_icon_url': get_weather_icon_url(cur_weather_data['weather'][0]['icon']),
        'current_description': cur_weather_data['weather'][0]['description'],
        "today_sunrise": datetime.fromtimestamp(cur_weather_data['sys']['sunrise']).time().strftime("%H:%M"),
        "today_sunset": datetime.fromtimestamp(cur_weather_data['sys']['sunset']).time().strftime("%H:%M"),
        'last_updated': last_updated,
        'forecast': []
    }

    # Extract forecast data for the next 5 days at the middle of the day
    for i in range(1, 6):
        # Get next day's date for the next 5 days
        next_day = time_now.date() + timedelta(days=i)

        # Set the time to 12:00 pm
        target_time = datetime.combine(next_day, datetime.strptime("12:00 PM", "%I:%M %p").time())
        # Extract the forecast data for the next 5 days at 12:00 pm
        for j in range(len(wforecast)):
            if str(target_time) == wforecast[j]['dt_txt']:
                timestamp = wforecast[j]['dt']
                dt = datetime.fromtimestamp(timestamp)
                day_name = dt.strftime("%A")
                forecast_data = {
                    'day': day_name,
                    'weather_condition': wforecast[j]['weather'][0]['description'],
                    'precipitation': wforecast[j]['pop'],
                    'temperature': int(wforecast[j]['main']['temp'])
                }
                weather_forecast['forecast'].append(forecast_data)
    
    top5_song_data = get_playlist_data(datasize=5)
    daily_song_data = get_playlist_data(datasize=50)
    # Get the product of the digits based on the current temperature
    m_num = multiply_digits(weather_forecast['current_temperature'])
    feature_daily_song_data = {
                'album_images': daily_song_data['album_images'][m_num],
                'song_names': daily_song_data['song_names'][m_num],
                'album_names': daily_song_data['album_names'][m_num],
                'artist_names': daily_song_data['artist_names'][m_num],
                }
    return render_template('home.html', weather_forecast=weather_forecast, top5_song_data=top5_song_data, feature_daily_song_data=feature_daily_song_data)


def get_weather_icon_url(icon_code: str) -> str:
    """Returns the URL of the weather icon image based on the icon code."""
    return f"http://openweathermap.org/img/w/{icon_code}.png"


def get_location(city_id=None, city_name=None):
    # Connect to the SQLite database
    conn = sqlite3.connect('citylist.db')
    cursor = conn.cursor()

    # Execute the query to retrieve data based on arguments
    if city_id:
        query = "SELECT state, country FROM cities WHERE id = ?"
        cursor.execute(query, (city_id,))
    elif city_name:
        parts = city_name.split(',')
        num_parts = len(parts)

        if num_parts >= 2:
            city = parts[0].strip()
            location = parts[1].strip()

            if len(location) == 2:
                # If it is a state code
                state = location.strip()
                country = ""
                query = "SELECT state, country FROM cities WHERE LOWER(name) = LOWER(?) AND LOWER(state) = LOWER(?)"
                cursor.execute(query, (city, state))
            else:
                # If it is a country code
                state = ""
                country = location.strip()
                query = "SELECT state, country FROM cities WHERE LOWER(name) = LOWER(?) AND LOWER(country) = LOWER(?)"
                cursor.execute(query, (city, country))
        elif num_parts == 1:
            city = parts[0].strip()
            query = "SELECT state, country FROM cities WHERE LOWER(name) = LOWER(?)"
            cursor.execute(query, (city,))
        else:
            return None, None
    else:
        return None, None

    result = cursor.fetchone()

    # Close the database connection
    conn.close()

    # Check if a matching record was found
    if result is not None:
        state, country = result
        return state, country
    else:
        return None, None


def get_playlist_data(datasize=None):
    playlist_id = '37i9dQZEVXbLp5XoPON0wI'
    playlist_data = retrieve_playlist_data(playlist_id)

    # Prepare the data for rendering in the template
    song_data = {
        'song_names': [],
        'artist_names': [],
        'popularity': [],
        'album_images': [],
        'album_names': [],
        'durations': [],
        'release_dates': []
    }

    for i in range(datasize):
        track = playlist_data['tracks']['items'][i]['track']
        song_data['song_names'].append(track['name'])

        artist_names = []
        for j in range(len(track['artists'])):
            artist_names.append(track['artists'][j]['name'])
        song_data['artist_names'].append(artist_names)

        song_data['popularity'].append(track['popularity'])
        song_data['album_images'].append(track['album']['images'][0]['url'])
        song_data['album_names'].append(track['album']['name'])
        # Convert duration from ms to mm:ss format
        duration_ms = track['duration_ms']
        duration_min = duration_ms // 60000
        duration_sec = (duration_ms % 60000) // 1000
        duration_formatted = f"{duration_min:02d}:{duration_sec:02d}"
        song_data['durations'].append(duration_formatted)
        song_data['release_dates'].append(track['album']['release_date'])
    
    return song_data


def multiply_digits(num):
    # Get the digits of the number
    digits = [int(digit) for digit in str(num)]

    # Multiply the digits
    product = 1
    for digit in digits:
        product *= digit

    while product > 50 and len(digits) > 1:
        digits = [int(digit) for digit in str(product)]
        product = 1
        for digit in digits:
            product *= digit

    return product


@app.route('/playlist')
def playlist_route():
    song_data = get_playlist_data(datasize=50)
    
    return render_template('playlist.html', song_data=song_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the username is already taken
        if UserModel.query.filter_by(email=email).first():
            flash('Username already exists')
            return redirect(url_for('register'))

        # Hash the password before storing it
        user = UserModel()
        user.setPassword(password)
        user.email = email
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form=LoginForm()
    # print(form.email.data)
    # print(form.password.data)
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('Please enter a valid email and password')
            return render_template('login.html',form=form)
        user = UserModel.query.filter_by(email = form.email.data ).first()
        if user is None:
            # print('User not found')
            flash('Please enter a valid email')
            return render_template('login.html',form=form)
        if not user.checkPassword(form.password.data):
            # print('Incorrect password')
            flash('Please enter a valid password')
            return render_template('login.html',form=form)
        login_user(user)
        # session['email'] = form.email.data
        # session['city'] = 'Seattle'
        return redirect(url_for('showWeather'))
    # This function will be called when someone accesses the root URL
    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    logout_user()
    session.pop('email', None)
    session.pop('city', None)
    # This function will be called when someone accesses the root URL
    return redirect(url_for('showLanding'))

# Run the application if this script is being run directly
if __name__ == '__main__':
    # The host is set to '0.0.0.0' to make the app accessible from any IP address.
    # The default port is 5000.
    app.run(host='0.0.0.0', debug='true', port=5000)
