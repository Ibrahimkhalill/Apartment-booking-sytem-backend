from django.shortcuts import render 
import requests
import datetime
def index(request):
    if 'city' in request.POST:
      city = request.POST['city']
      print(city)
      api = '16a767caf1f20eeaa53daf413b1e2d10'
      URL = 'https://api.openweathermap.org/data/2.5/weather'
      PARAMS = {'q':city,'api':api,'units':'metric'}

      r = requests.get(url=URL,params=PARAMS)
      res= r.json()
      print(res)
      # description = res['weather'][0]['description']
      # icon = res['weather'][0]['icon']
      # temp = res['main'][0]['temp']
      # day = datetime.date.today()
      # context = {
      #    "description":description,
      #    "icon": icon,
      #    "temp": temp,
      #    "day": day,
      #    "city": city,
      # }
      return render(request,'weatherapp/index.html')
    return render(request,'weatherapp/index.html')