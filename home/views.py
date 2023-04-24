from django.shortcuts import render, redirect
import requests
from .models import City
from .forms import CityForm

# Create your views here.
dic = {"previous_city_count": 0, "deleted_city_name": ''}

def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=c03afaccd8030b3947fc03cfeb3501f0'
    err_msg = ''
    message = ''
    message_class = ''
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name=new_city).count()
            if existing_city_count == 0:
                r = requests.get(url.format(new_city)).json()
                if r['cod'] == 200:
                    form.save()
                else:
                    err_msg = 'City does not exist in the world!'
            else:
                err_msg = 'City already exists in the list!'
        if err_msg:
            message = err_msg
            message_class = 'is-danger'
        else:
            message = 'City added successfully!'
            message_class = 'is-success'
            
    city_deleted_message = ''
    if City.objects.count() == dic["previous_city_count"] - 1:
        city_deleted_message = 'Succesfully deleted '
        message_class = 'is-success'
    dic["previous_city_count"] = City.objects.count()
    
    form = CityForm()
    cities = City.objects.all()
    weather_data = []
    for city in cities:
        r = requests.get(url.format(city)).json()
        city_weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
        weather_data.append(city_weather)
    context = {
        'weather_data' : weather_data, 
        'form' : form,
        'message' : message,
        'message_class' : message_class,
        'city_deleted_message': city_deleted_message,
        'deleted_city_name': dic["deleted_city_name"],
        }
    return render(request,'weather/index.html', context)

def delete_city(requests, city_name):
    dic["deleted_city_name"] = city_name
    City.objects.get(name=city_name).delete()
    return redirect('home')
