"""
Api for vodokanal info notify.

Created on 23.06.2018

@author: Ruslan Dolovanyuk

"""

import os
import requests

from bs4 import BeautifulSoup

from vodokanal.models import News


class Checker:
    """Class for get and check vodokanal news."""

    def __init__(self):
        """Initialize checker."""
        self.root = 'https://infoxvod.com.ua'

        self.news = []

    def load(self):
        """Load url for parse."""
        url = self.root + '/information/novosti'
        headers = {
            'User-Agent': 'Mozilla/5.0; Windows 8.1; rv:55.0; Firefox/55.0'
        }

        try:
            self.page = requests.get(url, headers=headers)
        except:
            return False
        return True

    def parse(self):
        """Parse html with BeautifulSoup4."""
        self.soup = BeautifulSoup(self.page.content, 'html.parser')
        self.news_list = self.soup.find_all('div', {'class': 'news_block'})
        self.news_list = [news.find('div', {'class': 'text'}) for news in self.news_list]

    def compare(self, last_title, last_date):
        """Compare all news with last saving news."""
        for news in self.news_list:
            news_dict = self.__get_data(news)
            if news_dict['title'] == last_title and news_dict['date'] == last_date:
                break
            else:
                self.news.insert(0, news_dict)

    def get_last(self):
        """Return data last news."""
        return self.__get_data(self.news_list[-1])

    def __get_data(self, news):
        """Return dict components from news."""
        news_dict = {}
        data = news.find_all('p')
        news_dict['title'] = news.find('h3').text
        news_dict['date'] = data[0].text
        news_dict['text'] = data[1].text
        news_dict['link_text'] = data[2].find('a').contents[0]
        news_dict['link_href'] = self.root + data[2].find('a').get('href')
        return news_dict


def common():
    """Common starting operations."""
    checker = Checker()
    if checker.load():
        checker.parse()
        return checker
    return None


def get_data(last_title, last_date):
    """Return components from all new news."""
    checker = common()
    if checker is None:
        return None
    checker.compare(last_title, last_date)
    return checker.news


def process(last_title, last_date, emails):
    """Main worker."""
    data = get_data(last_title, last_date)
    if (data is not None) and data:
        news_dict = data[-1]
        news = News.objects.last()
        if news is None:
            news = News(title=news_dict['title'], date=news_dict['date'], text=news_dict['text'], link_text=news_dict['link_text'], link_href=news_dict['link_href'])
        else:
            news.title = news_dict['title']
            news.date = news_dict['date']
            news.text = news_dict['text']
            news.link_text = news_dict['link_text']
            news.link_href = news_dict['link_href']
        news.save()
        for news_dict in data:
            #sender(news_dict, emails)
            pass


def sender(news_dict, emails):
    """Send email."""
    news = dict2html(news_dict)
    secret_key = os.environ.get('SECRET_KEY')
    subject = "Уведомление о новостях водоканала Одессы"
    for email in emails:
        post_data = {
                     'key': secret_key,
                     'subject': subject,
                     'email': email,
                     'message': news
                    }
        requests.post('http://site.ua/scripts/php/sender.php', data=post_data)


def dict2html(data):
    """Convert dict in html div news."""
    news = '''
              <html>
                <head>
                  <meta charset="utf-8">
                  <title>Уведомление о плановых отключениях водоканала города Одессы</title>
                </head>
                <body background="#7FFFD4" text="#343A40">
                  <div>
                    <div align="center"><h5 style="background: #007bff; color: #F8F9FA;">{title}</h5></div>
                    <div align="left"><p>{date}</p></div>
                    <div align="center"><p style="background: #50E2DA;">{text}</p></div>
                    <div align="right"><p><a href="{link_href}">{link_text}</a></p></div>
                  </div>
                  <div align="left">
                    <p>Данное сообщение вы получили, так как подписаны на сервис: <a href="http://elrusapps.herokuapp.com/vodokanal">Водоканал</a>.</p>
                    <p>Со всеми сервисами вы можете ознакомиться <a href="http://elrusapps.herokuapp.com">тут</a>.</p>
                    <p>Сайт автора: <a href="http://elrus.ho.ua">Руслан Долованюк</a>.</p>
                    <p>Также вы можете <a href="mailto:elrus-admin@s2.ho.ua">Написать письмо</a>.</p><br>
                  </div>
                </body>
              </html>
           '''.format(title=data['title'], date=data['date'], text=data['text'], link_text=data['link_text'], link_href=data['link_href'])
    return news


def test():
    """Run test geting last news components."""
    checker = common()
    if checker is None:
        print('Script complete error!')
    else:
        news_dict = checker.get_last()
        print('title: ' + news_dict['title'])
        print('date: ' + news_dict['date'])
        print('text: ' + news_dict['text'])
        print('link_text: ' + news_dict['link_text'])
        print('link_href: ' + news_dict['link_href'])


if __name__ == '__main__':
    test()
