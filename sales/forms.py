from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['industry', 'city', 'company_name', 'phone', 'online_booking', 'comment', 'website_link', 'map_link']
        widgets = {
            'industry': forms.TextInput(attrs={'placeholder': 'Сфера деятельности'}),
            'city': forms.TextInput(attrs={'placeholder': 'Город'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Наименование'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
            'online_booking': forms.TextInput(attrs={'placeholder': 'Ссылка на онлайн-запись'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Комментарий', 'rows': 24}),
            'website_link': forms.TextInput(attrs={'placeholder': 'https://example.com'}),
            'map_link': forms.TextInput(attrs={'placeholder': 'Ссылка на Яндекс/2ГИС'}),
        }
