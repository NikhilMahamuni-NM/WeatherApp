from django.shortcuts import render
from datetime import datetime, date, timedelta

from app.v1 import helpers

from app import utils

# Create your views here.

def home(request):

    context = {

    }

    return render(request, template_name="app/home.html", context=context)


def search(request):

    city = request.GET.get('city')

    print(f"Reqeusted City is --- {city}")

    weather_details = helpers.get_details(city=city)

    threshold_values = helpers.THRESHOLD_VALUES


    if weather_details:
        # Today Hour Details
        today_hour_details = weather_details.forecast_details[datetime.today().strftime("%Y-%m-%d")]
        hourly_details = []


        for hour in today_hour_details:
            details_json = today_hour_details[hour]
            details_json['time'] = hour

            hourly_details.append(details_json)


        # Forecast Details
        forecast_details = weather_details.forecast_details
        day_data = helpers.combine_hourly_data(api_data=forecast_details)
        forecast = helpers.aggregrate_hourly_data(day_data=day_data)
        

        # Last 24 Hours Details
        timings = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", 
                "12:00", "13:00","14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
        ]

        current_hour = f"{str(weather_details.weather_details['localtime'].split(' ')[-1][:2])}:00"
        print(f"Current Hour is ------- {current_hour} ---- position ---- {timings.index(current_hour)}")

        previous_hours_details = weather_details.previous_details

        timeline, aggregrated_values = helpers.get_last_hours_details(current_hour=current_hour, timings=timings, today_valid_hours=today_hour_details, previous_day=previous_hours_details)



        if weather_details.weather_details['temp_c'] > threshold_values['max_temp']:
            background_color = "#66A5AD"
        elif weather_details.weather_details['temp_c'] < threshold_values['min_temp']:
            background_color = "#a7adb2"	 
        else:
            background_color = "#8b929a"

        


        # context
        context = {
            "success": True,
            "city": city,
            "today_date": date.today(),
            "current_hour": f"{datetime.today().strftime('%Y-%m-%d')} {current_hour}",
            "threshold_values": threshold_values,
            "previous_date": date.today()-timedelta(days=1),
            "timeline": timeline[::-1],
            "last_hours_agg_values" : aggregrated_values,
            "details": weather_details,
            "background_color": background_color,
            "hourly_details": hourly_details,
            # "max_min": max_min,
            "forecast_details": forecast,
        }
    else:
        context = {
            "success": False,
            "city": city
        }
    return render(request, 'app/search.html', context=context)