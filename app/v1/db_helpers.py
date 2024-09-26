from app.models import WeatherDetails


def get_city_details(city):
    try:
        details = WeatherDetails.objects.get(city=city)
    except WeatherDetails.DoesNotExist:
        details = None
    
    return details


def set_city_details(city_name, weather_details, forecast_details, previous_details):
    try:
        city = WeatherDetails.objects.get(city=city_name)
    except:
        city = WeatherDetails()
        city.city = city_name

    city.weather_details = weather_details
    city.forecast_details = forecast_details
    city.previous_details = previous_details
    city.save()

    return city

