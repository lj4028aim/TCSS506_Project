import gzip
import json
import sqlite3

"""
The following code is used to create a SQLite database from the gzipped JSON file retrieved from OpenWeatherMap.
"""
# Read the gzipped JSON file
def read_gzipped_json_file(file_path):
    with gzip.open(file_path, 'rt', encoding='utf-8') as file:
        return json.load(file)

# Create an SQLite database and table
def create_database(database_name):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            name TEXT,
            state TEXT,
            country TEXT,
            lon REAL,
            lat REAL
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into the SQLite database
def insert_data(database_name, data):
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO cities (id, name, state, country, lon, lat)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

# Specify the path to the gzipped JSON file
gzipped_json_file = 'city.list.json.gz'

# Specify the name of the SQLite database
database_name = 'citylist.db'

# Read the gzipped JSON file
json_data = read_gzipped_json_file(gzipped_json_file)

# Create the SQLite database and table
create_database(database_name)

# Prepare the data for insertion
data = []
for item in json_data:
    city_data = (
        item['id'],
        item['name'],
        item.get('state', ''),
        item.get('country', ''),
        item['coord']['lon'],
        item['coord']['lat']
    )
    data.append(city_data)

# Insert the data into the SQLite database
insert_data(database_name, data)