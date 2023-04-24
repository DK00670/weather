from django.shortcuts import render, redirect
import requests
from django.contrib import messages
from .models import City
from .forms import CityForm

# Create your views here.

def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=c03afaccd8030b3947fc03cfeb3501f0'
    err_msg = ''
    if request.method == 'POST':
        form = CityForm(request.POST)
    else:
        form = CityForm(request.GET)
    
    if form.is_valid():
        new_city = form.cleaned_data['name']
        existing_city_count = City.objects.filter(name=new_city).count()
        if existing_city_count == 0:
            r = requests.get(url.format(new_city)).json()
            if r['cod'] == 200:
                form.save()
                list(messages.get_messages(request))
                messages.success(request, 'City added successfully!')
            else:
                list(messages.get_messages(request))
                messages.error(request, 'City does not exist in the world!')
        else:
            list(messages.get_messages(request))
            messages.error(request, 'City already exists in the list!')

    
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
        }
    return render(request,'home/index.html', context)

def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    list(messages.get_messages(request))
    messages.success(request, 'Successfully deleted {}'.format(city_name))
    return redirect('index')
