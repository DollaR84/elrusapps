from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext

# Create your views here.

import json

from .models import Weather
from subscribers.models import Subscribers

from subscribers.forms import SubscribeForm


def index(request):
    if 'POST' == request.method:
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscriber = Subscribers.objects.filter(subscriber=form.cleaned_data['email']).first()
            if (subscriber is not None) and subscriber.weather:
                form.add_error(None, 'Данный email уже подписан на уведомления')
            else:
                if subscriber is None:
                    subscriber = Subscribers(subscriber=form.cleaned_data['email'], weather=True)
                else:
                    subscriber.weather = True
                subscriber.save()
                messages.success(request, 'Ваш email успешно подписан.')
                messages.success(request, 'Спасибо за использование нашего сервиса.')
    else:
        form = SubscribeForm()

    weather = {}
    try:
        data = Weather.objects.all().filter(id=1).first()
        weather['today'] = json.loads(data.today)
        weather['days'] = json.loads(data.days)
        weather['water'] = json.loads(data.water)
        weather['infoDaylight'] = json.loads(data.infoDaylight)
        weather['warnings'] = data.warnings
        weather['description'] = data.description
    except:
        weather['today'] = {}
        weather['days'] = []
        weather['water'] = {}
        weather['infoDaylight'] = {}
        weather['warnings'] = ''
        weather['description'] = ''
    context = RequestContext(request, {
                                        'form': form,
                                        'weather': weather
                                      })
    return render(request, 'weather/index.html', context.flatten())
