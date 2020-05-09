"""subscribers forms

"""

from django import forms


class SubscribeForm(forms.Form):
    email = forms.EmailField(label='Почта', help_text='Введите свой email для подписки на уведомления')

    def clean_email(self):
        data = self.cleaned_data['email']
        return data
