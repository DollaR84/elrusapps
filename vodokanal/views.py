from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext

# Create your views here.

from .models import News
from subscribers.models import Subscribers

from subscribers.forms import SubscribeForm

def index(request):
    if 'POST' == request.method:
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subscriber = Subscribers.objects.filter(subscriber=form.cleaned_data['email']).first()
            if (subscriber is not None) and subscriber.vodokanal:
                form.add_error(None, 'Данный email уже подписан на уведомления')
            else:
                if subscriber is None:
                    subscriber = Subscribers(subscriber=form.cleaned_data['email'], vodokanal=True)
                else:
                    subscriber.vodokanal = True
                subscriber.save()
                messages.success(request, 'Ваш email успешно подписан.')
                messages.success(request, 'Спасибо за использование нашего сервиса.')
    else:
        form = SubscribeForm()
    last_news = News.objects.last()
    context = RequestContext(request, {
                                        'form': form,
                                        'last_news': last_news
                                      })
    return render(request, 'vodokanal/index.html', context.flatten())
