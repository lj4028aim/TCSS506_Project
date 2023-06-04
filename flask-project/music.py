import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def retrieve_playlist_data(playlist_id):
    # client ID and client secret
    client_id = '28a872dca3a6411eb808ea34d9fd5f54'
    client_secret = '3e851b68ff7847cabdc831c4ad166b1b'

    # Create an instance of the Spotify client
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Retrieve playlist data
    playlist = sp.playlist(playlist_id)
    
    # Uncomment section below to write playlist data to a JSON file for debugging purposes if needed
    # with open('playlist.json', 'w') as file:
    #     json.dump(playlist, file, indent=4)

    # print("Data written to playlist.json successfully.")

    return playlist


if __name__ == "__main__":
    # Playlist ID for TOP 50 USA accrued from Spotify
    playlist_id = '37i9dQZEVXbLp5XoPON0wI'

    # Retrieve playlist data
    playlist_data = retrieve_playlist_data(playlist_id)
