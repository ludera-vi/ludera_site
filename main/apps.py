from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        from django.urls import register_converter
        from .converters import UnicodeSlugConverter
        register_converter(UnicodeSlugConverter, 'uslug')
