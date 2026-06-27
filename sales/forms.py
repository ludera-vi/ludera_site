from django import forms
from .models import Client, LEGAL_STATUSES


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['industry', 'city', 'company_name', 'name', 'phone', 'legal_status', 'comment']
        widgets = {
            'industry': forms.TextInput(attrs={'placeholder': 'Сфера деятельности'}),
            'city': forms.TextInput(attrs={'placeholder': 'Город'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Наименование'}),
            'name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Телефон'}),
            'comment': forms.Textarea(attrs={'placeholder': 'Комментарий', 'rows': 3}),
        }
