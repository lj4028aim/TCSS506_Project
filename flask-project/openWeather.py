import requests

def get_weather(term="", city="Tacoma", state="Washington", country="US", units="metric", api_key="b8ba2e29e69c2c019ba93623a385ff4e"):
    search_api_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{state},{country}&units={units}&appid={api_key}"
    response = requests.get(search_api_url, timeout=5)
    data = response.json()
    return data

if __name__ == '__main__':
    # Example usage
    weather_data = get_weather(city="Tacoma", state="Washington", country="US")
    print(weather_data)

    # Test with a different city and state (New York, NY)
    # weather_data = get_weather(city="Seattle", state="WA")
    # print(weather_data)
    