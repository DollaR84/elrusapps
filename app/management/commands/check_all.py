"""
Check command for manage.py.

Created on 30.06.2018
modifyed 08.05.2020 (change update weather on sinoptik)

@author: Ruslan Dolovanyuk

"""

import json

from datetime import datetime

from django.core.management.base import BaseCommand

from vodokanal.models import News
from vodokanal.news import process

from weather.models import Weather
from weather.models import UpdateDay
from weather.weather import Sinoptik
from weather.weather import get_weather
from weather.weather import sender

from subscribers.models import Subscribers


class Command(BaseCommand):
    help = 'Check news infoxvod and weather and notify subscribers.'

    def handle(self, *args, **options):
        self.check_news()
        #self.check_weather()
        self.check_sinoptik()

    def check_news(self):
        last_news = News.objects.last()
        title = '' if last_news is None else last_news.title
        date = '' if last_news is None else last_news.date
        try:
            emails = [subscriber.subscriber for subscriber in Subscribers.objects.all() if subscriber.vodokanal]
        except:
            emails = []
        process(title, date, emails)

    def check_weather(self):
        """Check and process weather data."""
        date = datetime.strftime(datetime.now(), "%d.%m.%Y")
        row = Simple.objects.all().filter(id=1).first()
        if row is None:
            row = Simple(data=date)
        else:
            if date == row.data:
                return
            else:
                row.data = date
        row.save()
        weather = get_weather()

        for data in weather['simple']:
            row = Simple.objects.all().filter(id=data['period']+1).first()
            if row is None:
                row = Simple(data=json.dumps(data))
            else:
                row.data = json.dumps(data)
            row.save()

        try:
            emails = [subscriber.subscriber for subscriber in Subscribers.objects.all() if subscriber.weather]
        except:
            emails = []
        sender(weather['simple'][1], emails)

    def check_sinoptik(self):
        """Check and process weather data from sinoptik.ua."""
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        last_update = UpdateDay.objects.all().filter(id=1).first()
        if (last_update is None) or (last_update.day != date):
            weather = Sinoptik()
            if weather.load():
                weather.get_weather()

                weather_db = Weather.objects.all().filter(id=1).first()
                if weather_db is None:
                    weather_db = Weather(
                                         today=weather.today_str(),
                                         days=weather.days_str(),
                                         water=weather.water_str(),
                                         infoDaylight=weather.infoDaylight_str(),
                                         warnings=weather.warnings,
                                         description=weather.description
                                        )
                else:
                    weather_db.today = weather.today_str()
                    weather_db.days = weather.days_str()
                    weather_db.water = weather.water_str()
                    weather_db.infoDaylight = weather.infoDaylight_str()
                    weather_db.warnings = weather.warnings
                    weather_db.description = weather.description
                weather_db.save()

                if last_update is None:
                    last_update = UpdateDay(day=date)
                else:
                    last_update.day = date
                last_update.save()
