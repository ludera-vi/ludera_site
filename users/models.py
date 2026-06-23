from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from main.models import Product


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    email_verified = models.BooleanField('Email подтверждён', default=False)
    phone_verified = models.BooleanField('Телефон подтверждён', default=False)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.email or self.user.username}'

    def get_active_products(self):
        return UserProduct.objects.filter(user=self.user, is_active=True)

    def product_access(self, product):
        return UserProduct.objects.filter(user=self.user, product=product, is_active=True).exists()


class UserProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_products', verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='assigned_users', verbose_name='Товар')
    is_active = models.BooleanField('Активен', default=True)
    purchased_at = models.DateTimeField('Дата покупки', default=timezone.now)
    expires_at = models.DateTimeField('Истекает', blank=True, null=True)

    class Meta:
        verbose_name = 'Товар пользователя'
        verbose_name_plural = 'Товары пользователей'
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.email} — {self.product.title}'


class ProductFile(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='files', verbose_name='Товар')
    title = models.CharField('Название', max_length=300)
    file = models.FileField('Файл', upload_to='product_files/')
    file_type = models.CharField('Тип файла', max_length=100, blank=True, help_text='Напр., PDF, Видео, Архив')
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Файл продукта'
        verbose_name_plural = 'Файлы продуктов'

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return self.file.name.split('/')[-1] if self.file else ''


class UserSetting(models.Model):
    name = models.CharField('Название', max_length=200)
    value = models.TextField('Значение', blank=True)
    is_active = models.BooleanField('Активно', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Настройка пользовательского кабинета'
        verbose_name_plural = 'Настройки пользовательского кабинета'

    def __str__(self):
        return self.name


class Goods(models.Model):
    title = models.CharField('Название', max_length=300)
    subtitle = models.CharField('Подзаголовок', max_length=500, blank=True)
    description = models.TextField('Описание', blank=True)
    content = models.TextField('Контент (HTML)', blank=True,
        help_text='Полный текст с форматированием, кодом, изображениями, видео')
    badge_text = models.CharField('Текст бейджа', max_length=50, blank=True, default='')
    accent_color = models.CharField('Цвет акцента', max_length=20, default='#2d8f5e')
    order = models.IntegerField('Порядок', default=0)
    is_visible = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title


class GoodsFile(models.Model):
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='files', verbose_name='Товар')
    title = models.CharField('Название', max_length=300)
    file = models.FileField('Файл', upload_to='goods_files/')
    file_type = models.CharField('Тип файла', max_length=100, blank=True,
        help_text='Напр., PDF, Видео, Архив, Инструкция')
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Добавлен', auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Файл товара'
        verbose_name_plural = 'Файлы товаров'

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return self.file.name.split('/')[-1] if self.file else ''


class CabinetPermission(models.Model):
    SECTIONS = [
        ('dashboard', 'Дашборд'),
        ('services', 'Услуги'),
        ('products', 'Продукты'),
        ('goods', 'Товары'),
        ('projects', 'Проекты'),
        ('blog', 'Блог'),
        ('contacts', 'Заявки'),
        ('pageviews', 'Просмотры'),
        ('structure', 'Структура'),
        ('users', 'Пользователи'),
        ('settings', 'Настройки'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cabinet_permissions', verbose_name='Пользователь')
    section = models.CharField('Раздел', max_length=50, choices=SECTIONS)

    class Meta:
        verbose_name = 'Право доступа к разделу'
        verbose_name_plural = 'Права доступа к разделам'
        unique_together = ('user', 'section')

    def __str__(self):
        return f'{self.user.email} — {self.get_section_display()}'


class UserGoods(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_goods', verbose_name='Пользователь')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='assigned_users', verbose_name='Товар')
    is_active = models.BooleanField('Активен', default=True)
    purchased_at = models.DateTimeField('Дата покупки', default=timezone.now)
    expires_at = models.DateTimeField('Истекает', blank=True, null=True)

    class Meta:
        verbose_name = 'Товар пользователя'
        verbose_name_plural = 'Товары пользователей'
        unique_together = ('user', 'goods')

    def __str__(self):
        return f'{self.user.email} — {self.goods.title}'
