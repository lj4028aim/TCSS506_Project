import sqlite3

def display_top_songs():
    # Connect to the SQLite database
    conn = sqlite3.connect('playlist.db')
    cursor = conn.cursor()

    # Execute the query to retrieve the top 5 songs
    query = "SELECT id, key, value FROM playlist_data;"
    cursor.execute(query)

    # Fetch the results
    results = cursor.fetchall()

    # Iterate through the results and display them
    values = []
    for row in results:
        # id = row[0]
        # key = row[1]
        value = row[2]
    value = list(value)
    print(value)


    # Close the database connection
    conn.close()

if __name__ == "__main__":
    # Call the function to display the top songs
    display_top_songs()
