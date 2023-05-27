import requests

def get_weather(term="", city="Tacoma", state="Washington", country="US", units="metric", api_key="b8ba2e29e69c2c019ba93623a385ff4e"):
    """
    Get the weather forecast for a given city, state, and country.
    """
    search_api_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city},{state},{country}&units={units}&appid={api_key}"
    response = requests.get(search_api_url, timeout=5)
    data = response.json()
    return data

def get_cur_weather(term="", city="Tacoma", state="Washington", country="US", units="metric", api_key="b8ba2e29e69c2c019ba93623a385ff4e"):
    """
    Get the current weather for a given city, state, and country.
    """
    search_api_url_cur = f"http://api.openweathermap.org/data/2.5/weather?q={city},{state},{country}&units={units}&appid={api_key}"
    cur_response = requests.get(search_api_url_cur, timeout=5)
    cur_data = cur_response.json()
    return cur_data

if __name__ == '__main__':
    cur_weather_data = get_cur_weather()
    weather_data = get_weather()
    # print(cur_weather_data)
    # print(weather_data)
    