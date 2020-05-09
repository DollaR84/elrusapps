"""
Module of weather functions elrusapps project.

Created on 20.07.2018
modified on 06.05.2020 (create class SINOPTIK)

@author: Ruslan Dolovanyuk

"""

import json
import os
import requests
import urllib.request

from bs4 import BeautifulSoup


class Sinoptik:
    """Class for getting weather from site sinoptik.ua."""

    def __init__(self):
        """Initialize class."""
        self.__url = 'https://sinoptik.ua/%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0-%D0%BE%D0%B4%D0%B5%D1%81%D1%81%D0%B0'
        self.__headers = {
            'User-Agent': 'Mozilla/5.0; Windows 8.1; rv:55.0; Firefox/55.0'
        }

    def load(self):
        """Loading site for parse."""
        try:
            self.__page = requests.get(self.__url, headers=self.__headers)
        except:
            return False
        return True

    def get_weather(self):
        """Parse html with BeautifulSoup4."""
        self.__bs = BeautifulSoup(self.__page.content, 'html.parser')
        tabs = self.__bs.find('div', {'class': 'tabs'})
        self.__today = self.__get_today(tabs.find('div', {'class': 'main loaded'}))
        self.__days = self.__get_days(tabs.find_all('div', {'class': 'main '}))

        tabsContent = self.__bs.find('div', {'class': 'tabsContent'})
        self.__water = self.__get_water(tabsContent.find('p', {'class': 'today-water'}))
        self.__infoDaylight = self.__get_infoDaylight(tabsContent.find('div', {'class': 'infoDaylight'}))
        self.__warnings = self.__get_warnings(tabsContent.find('div', {'class': 'oWarnings clearfix'}).find('div', {'class': 'description'}))
        self.__description = self.__get_description(tabsContent.find('div', {'class': 'wDescription clearfix'}).find('div', {'class': 'description'}))

    def __get_day(self, bsObj, today=False):
        """Return day dict from bs object."""
        day = {}
        day['id'] = bsObj['id'][-1]
        day_link = bsObj.find('p', {'class': 'day-link'}) if today else bsObj.find('a', {'class': 'day-link'})
        day['weekday'] = day_link.text
        day['date_full'] = day_link['data-link'].split('/')[-1]
        day['year'] = day['date_full'].split('-')[0]
        day['date'] = bsObj.find('p', {'class': 'date'}).text
        day['month'] = bsObj.find('p', {'class': 'month'}).text

        weatherIco = bsObj.find('div', {'class': 'weatherIco'})
        weatherImg = weatherIco.find('img')
        day['weatherIco_title'] = weatherIco['title']
        day['weatherImg'] = {'alt': weatherImg['alt'], 'src': weatherImg['src']}

        temp = bsObj.find('div', {'class': 'temperature'})
        min = temp.find('div', {'class': 'min'})
        max = temp.find('div', {'class': 'max'})
        day['min'] = {'text': min.text, 'temp': min.find('span').text}
        day['max'] = {'text': max.text, 'temp': max.find('span').text}
        return day

    def __get_today(self, bsObj):
        """Return today dict from bs object."""
        return self.__get_day(bsObj, True)

    def __get_days(self, bsObj_list):
        """Return days list dicts from bs object."""
        return [self.__get_day(bsObj) for bsObj in bsObj_list]

    def __get_water(self, bsObj):
        """Return water dict from bs object."""
        water = {}
        img = bsObj.find('img')
        water['temp'] = {'text': bsObj.text, 'temp': bsObj.find('span').text}
        water['img'] = {'alt': img['alt'], 'height': img['height'], 'width': img['width'], 'src': img['src']}
        return water

    def __get_infoDaylight(self, bsObj):
        """Return infoDaylight dict from bs object."""
        times = bsObj.find_all('span')
        return {'text': bsObj.text, 'sunrise': times[0].text, 'sunset': times[1].text}

    def __get_warnings(self, bsObj):
        """Return warnings string from bs object."""
        return bsObj.text

    def __get_description(self, bsObj):
        """Return description string from bs object."""
        return bsObj.text

    @property
    def today(self):
        """Return today dict."""
        return self.__today

    @property
    def days(self):
        """Return list days dicts."""
        return self.__days

    @property
    def water(self):
        """Return water dict."""
        return self.__water

    @property
    def infoDaylight(self):
        """Return infoDaylight dict."""
        return self.__infoDaylight

    @property
    def warnings(self):
        """Return warnings string."""
        return self.__warnings

    @property
    def description(self):
        """Return description string."""
        return self.__description

    def today_str(self):
        """Return today dict in json string for saving bd."""
        return json.dumps(self.__today)

    def days_str(self):
        """Return list days dicts in json str for saving bd."""
        return json.dumps(self.__days)

    def water_str(self):
        """Return water dict in json string for saving bd."""
        return json.dumps(self.__water)

    def infoDaylight_str(self):
        """Return infoDaylight dict in json str for saving bd."""
        return json.dumps(self.__infoDaylight)


def main():
    weather = Sinoptik()
    if weather.load():
        weather.get_weather()
        print(weather.today['date_full'])


def get_weather():
    """Get data weather struct from wunderground."""
    weather = {}
    wunderground_api_key = os.environ.get('WUNDERGROUND_API_KEY')
    url = 'http://api.wunderground.com/api/%s/forecast/lang:RU/q/UA/Odessa.json' % wunderground_api_key

    http_data = urllib.request.urlopen(url)
    data = json.loads(http_data.read().decode('utf8'))
    http_data.close()

    simple = json.dumps(data['forecast']['simpleforecast']['forecastday'])
    weather['simple'] = json.loads(simple.replace('null', '0'))
    for simple in weather['simple']:
        if '' == simple['avewind']['dir']:
            simple['avewind']['dir'] = 'Неопределенно'
        if '' == simple['maxwind']['dir']:
            simple['maxwind']['dir'] = 'Неопределенно'
    return weather


def sender(weather, emails):
    """Send email."""
    date = '%d %s %d, %s' % (weather['date']['day'], weather['date']['monthname'], weather['date']['year'], weather['date']['weekday'])
    msg = __get_message(weather, date)
    secret_key = os.environ.get('SECRET_KEY')
    subject = "Уведомление о погоде Одессы %s" % date
    for email in emails:
        post_data = {
                     'key': secret_key,
                     'subject': subject,
                     'email': email,
                     'message': msg
                    }
        requests.post('http://host.ua/scripts/php/sender.php', data=post_data)


def __get_message(weather, date):
    """Return formatting message weather for send emails."""
    if weather['snow_allday']['in'] > weather['qpf_allday']['in']:
        pop_level = 'Уровень снега: {0}см (днем: {1}см, ночью: {2}см)'.format(weather['snow_allday']['cm'], weather['snow_day']['cm'], weather['snow_night']['cm'])
    else:
        pop_level = 'Уровень осадков: {0}мм (днем: {1}мм, ночью: {2}мм)'.format(weather['qpf_allday']['mm'], weather['qpf_day']['mm'], weather['qpf_night']['mm'])
    msg = '''
              <html>
                <head>
                  <meta charset="utf-8">
                  <title>Уведомление о погоде города Одессы</title>
                </head>
                <body background="#7FFFD4" text="#343A40">
                  <div>
                    <div align="center"><h5 style="background: #007bff; color: #F8F9FA;">{title}</h5></div>
                    <div align="left">
                      <img style="float: left; margin: 10px 10px 10px 0;" src="{icon_url}" alt="{icon}" >
                      <p>{conditions}<br>
                      Температура: {low}°C - {high}°C<br>
                      Вероятность осадков: {pop}%<br>
                      {level}<br>
                      Средний ветер: {avewind}км/ч, направление: {avewind_dir} или {avewind_degrees}°<br>
                      Максимальный ветер: {maxwind}км/ч, направление: {maxwind_dir} или {maxwind_degrees}°<br>
                      Влажность: {avehumidity}%<br></p>
                    </div>
                  </div>
                  <div align="left">
                    <p>Данное сообщение вы получили, так как подписаны на сервис: <a href="http://elrusapps.herokuapp.com/weather">Погода</a>.</p>
                    <p>Со всеми сервисами вы можете ознакомиться <a href="http://elrusapps.herokuapp.com">тут</a>.</p>
                    <p>Сайт автора: <a href="http://elrus.ho.ua">Руслан Долованюк</a>.</p>
                    <p>Также вы можете <a href="mailto:elrus-admin@s2.ho.ua">Написать письмо</a>.</p><br>
                  </div>
                </body>
              </html>
          '''.format(title=date,
                     icon_url=weather['icon_url'],
                     icon=weather['icon'],
                     conditions=weather['conditions'],
                     low=weather['low']['celsius'],
                     high=weather['high']['celsius'],
                     pop=weather['pop'],
                     level=pop_level,
                     avewind=weather['avewind']['kph'],
                     avewind_dir=weather['avewind']['dir'],
                     avewind_degrees=weather['avewind']['degrees'],
                     maxwind=weather['maxwind']['kph'],
                     maxwind_dir=weather['maxwind']['dir'],
                     maxwind_degrees=weather['maxwind']['degrees'],
                     avehumidity=weather['avehumidity'])
    return msg


if __name__ == '__main__':
    main()
