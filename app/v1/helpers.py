import requests

from datetime import date, timedelta


from app.v1 import db_helpers
from app import utils


API_KEY = "4943144aa2c642d68b1120130241709"

FORECAST_DAYS = "7"

THRESHOLD_VALUES = {
    "max_temp": 30,
    "min_temp": 19,
    
    "max_humidity": 80,
    "min_humidity": 30,
    "max_rainfall_start": 4,
    "max_rainfall_end": 8,
    
    "light_rainfall_start": 0.03,
    "light_rainfall_end": 4,

    "light_wind": 4,
    "gentle_wind_start": 5,
    "gentle_wind_end": 20,
    "moderate_wind_start": 21,
    "moderate_wind_end": 30,
    "high_wind": 31,

    "min_uv_index_start": 0,
    "min_uv_index_end": 2,

    "mod_uv_index_start": 3,
    "mod_uv_index_end": 7,

    "max_uv_index_threshold": 8,
    


    "max_aqi": 50
}

def fetch_weather_details(city):
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days={FORECAST_DAYS}"

        response = requests.get(url=url)
        
        if response.status_code == 200:
            details = response.json()
        else:
            details = None
    

        return details
    except Exception as e:
        print(f"Connection Request Failed Due to ----- {e}")
        return None

def fetch_day_before_details(city, date):
    url = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q={city}&dt={date}"

    response = requests.get(url=url)
    
    if response.status_code == 200:
        details = response.json()
    else:
        details = None
    

    return details


def get_weather_details(city):
    
    api_details = fetch_weather_details(city=city)

    if api_details:
        weather_details = process_weather_details(api_data=api_details)
        forecast_details= process_forecast_details(api_data=api_details)

        yesterday_date = date.today() - timedelta(days=1)
        fetch_previous_details = fetch_day_before_details(city=city, date=yesterday_date)

        previous_details = process_previous_details(api_data=fetch_previous_details)

        city_details = db_helpers.set_city_details(city_name=city, weather_details=weather_details, forecast_details=forecast_details, previous_details=previous_details)

    else:
        city_details = None

    return city_details



def get_details(city):

    city_details = get_weather_details(city=city)

    if city_details:
        return city_details
    else:
        db_details = db_helpers.get_city_details(city=city)

        if db_details:
            return db_details
        else:
            return None



def process_weather_details(api_data):
    location_details = api_data['location']

    current_details = api_data['current']

    weather_details = {
        "region": location_details['region'],
        "country": location_details['country'],
        "latitude": location_details['lat'],
        "longitude": location_details['lon'],
        "timezone": location_details['tz_id'],
        "localtime": location_details['localtime'],

        "temp_c": current_details['temp_c'],
        "temp_f": current_details['temp_f'],
        "is_day": current_details['is_day'],
        "weather_desc": current_details['condition']['text'],
        "weather_icon": f"https://{current_details['condition']['icon'][2:]}",
        "wind_mph": current_details['wind_mph'],
        "wind_kph": current_details['wind_kph'],
        "wind_dir": current_details['wind_dir'],
        "pressure_mb": current_details['pressure_mb'],
        "pressure_in": current_details['pressure_in'],
        "precip_mm": current_details['precip_mm'],
        "precip_in": current_details['precip_in'],
        "humidity": current_details['humidity'],
        "cloud": current_details['cloud'],
        "uv": current_details['uv'],
    }

    return weather_details

def process_forecast_details(api_data):

    forecast_details = {}

    for day in api_data['forecast']['forecastday']:
        hourly_details = day['hour']
        hourly_data = get_hourly_json(api_data=hourly_details)
    
        forecast_details[day['date']] = hourly_data
    
    # print(f"Forecast Details ------ {forecast_details}")

    return forecast_details



def process_previous_details(api_data):

    day = api_data['forecast']['forecastday'][0]
    date = day['date']
    # print(f"\n\n\n\n\n\n\n\nPrevious Date is ---- {date}\n\n\n\n\n\n")
    hourly_details = day['hour']

    previous_details = {date: get_hourly_json(hourly_details)}

    # print(f"\n\n\n\nPrevious Details ------ {previous_details}")

    return previous_details




def get_hourly_json(api_data):
    hourly_data= {}

    for data in api_data:
        details_json = {}

        details_json['temp_c'] = data['temp_c']
        details_json['temp_f'] = data['temp_f']
        details_json['weather_desc'] = data['condition']['text']
        details_json['weather_icon'] = f"https://{data['condition']['icon'][2:]}"
        details_json['wind_kph'] = data['wind_kph']
        details_json['pressure_mb'] = data['pressure_mb']
        details_json['precip_mm'] = data['precip_mm']
        details_json['humidity'] = data['humidity']
        details_json['cloud'] = data['cloud']
        details_json['uv'] = data['uv']


        hourly_data[str(data['time']).split(" ")[-1]] = details_json

    return hourly_data



def combine_hourly_data(api_data):
    
    day_data = {}

    for day in api_data:
        # print(f"\n\n\nDay --- {day}")
        details_json = {
            "temp_c": [],
            "temp_f": [],
            "weather_desc": [],
            "weather_icon": [],
            "wind_kph": [],
            "pressure_mb": [],
            "precip_mm": [],
            "humidity": [],
            "cloud": [],
            "uv": []
        }

        day_json = api_data[day]
        for hour in day_json:
            hour_data = day_json[hour]
            details_json['temp_c'].append(hour_data['temp_c'])
            details_json['temp_f'].append(hour_data['temp_f'])
            details_json['weather_desc'].append(hour_data['weather_desc'])
            details_json['weather_icon'].append(hour_data['weather_icon'])
            details_json['wind_kph'].append(hour_data['wind_kph'])
            details_json['pressure_mb'].append(hour_data['pressure_mb'])
            details_json['precip_mm'].append(hour_data['precip_mm'])
            details_json['humidity'].append(hour_data['humidity'])
            details_json['cloud'].append(hour_data['cloud'])
            details_json['uv'].append(hour_data['uv'])
        
        day_data[day] = details_json

    return day_data


def aggregrate_hourly_data(day_data):
    forecast = []
    
    for day in day_data:
        json_details = {}
        json_details['date'] = day
        json_details['temp_c'] = utils.get_avg(day_data[day]['temp_c'])
        json_details['temp_f'] = utils.get_avg(day_data[day]['temp_f'])
        json_details['weather_desc'] = utils.get_max_occurring_value(day_data[day]['weather_desc'])
        json_details['weather_icon'] = day_data[day]['weather_icon'][day_data[day]['weather_desc'].index(utils.get_max_occurring_value(day_data[day]['weather_desc']))]
        json_details['wind'] = utils.get_avg(day_data[day]['wind_kph'])
        json_details['pressure'] = utils.get_avg(day_data[day]['pressure_mb'])
        json_details['precipitation'] = utils.get_avg(day_data[day]['precip_mm'])
        json_details['humidity'] = f"{utils.get_avg(day_data[day]['humidity'])}"
        json_details['cloud'] = f"{utils.get_avg(day_data[day]['cloud'])}"
        json_details['uv'] = f"{utils.get_avg(day_data[day]['uv'])}"

        forecast.append(json_details)

    # print(f"Aggregrate Data --- {forecast}")

    return forecast


def get_last_hours_details(current_hour, timings, today_valid_hours, previous_day):

    today_hours = timings[:(timings.index(current_hour))+1][::-1]
    prev_day_hours = timings[timings.index(current_hour)+1:][::-1]
    
    today_date= date.today()
    previous_date = today_date-timedelta(days=1)

    print(f"Today day Hours ----- {len(today_hours)} --- {today_hours}")
    print(f"Previous Day Hours ----- {len(prev_day_hours)} --- {prev_day_hours}")

    timeline = []


    for hour in today_hours:
        today_valid_json = today_valid_hours[hour]
        today_valid_json['curr_time'] = f"{today_date} {hour}"

        timeline.append(today_valid_json)


    for hour in prev_day_hours:
        prev_day_json = previous_day[previous_date.strftime("%Y-%m-%d")][hour]
        prev_day_json['curr_time'] = f"{previous_date} {hour}"

        timeline.append(prev_day_json)
    
    # print(f"Last 24 hours Timeline ---- {timeline}")

    aggregrated_values = get_aggregrated_values(last_weather_data=timeline)

    # print(f"Last 24 hours Aggregrated Values ---- {aggregrated_values}")

    return timeline, aggregrated_values


def get_aggregrated_values(last_weather_data):
    details_json = {
        "temp_c": [],
        "temp_f": [],
        "weather_desc": [],
        "weather_icon": [],
        "wind_kph": [],
        "pressure_mb": [],
        "precip_mm": [],
        "humidity": [],
        "cloud": [],
        "uv": []
    }

    for hour_data in last_weather_data:

        details_json['temp_c'].append(hour_data['temp_c'])
        details_json['temp_f'].append(hour_data['temp_f'])
        details_json['weather_desc'].append(hour_data['weather_desc'])
        details_json['weather_icon'].append(hour_data['weather_icon'])
        details_json['wind_kph'].append(hour_data['wind_kph'])
        details_json['pressure_mb'].append(hour_data['pressure_mb'])
        details_json['precip_mm'].append(hour_data['precip_mm'])
        details_json['humidity'].append(hour_data['humidity'])
        details_json['cloud'].append(hour_data['cloud'])
        details_json['uv'].append(hour_data['uv'])

    aggregate_values = {}
    aggregate_values['temp_c'] = utils.get_avg(details_json['temp_c'])
    aggregate_values['temp_f'] = utils.get_avg(details_json['temp_f'])
    aggregate_values['weather_desc'] = utils.get_max_occurring_value(details_json['weather_desc'])
    aggregate_values['weather_icon'] = details_json['weather_icon'][details_json['weather_desc'].index(utils.get_max_occurring_value(details_json['weather_desc']))]
    aggregate_values['wind_kph'] = utils.get_avg(details_json['wind_kph'])
    aggregate_values['pressure_mb'] = utils.get_avg(details_json['pressure_mb'])
    aggregate_values['precip_mm'] = utils.get_avg(details_json['precip_mm'])
    aggregate_values['humidity'] = f"{utils.get_avg(details_json['humidity'])}"
    aggregate_values['cloud'] = f"{utils.get_avg(details_json['cloud'])}"
    aggregate_values['uv'] = f"{utils.get_avg(details_json['uv'])}"

    # print(f"After ---- Details Json ----- {aggregate_values}")

    return aggregate_values