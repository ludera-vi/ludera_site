from django.db import models
from django.contrib.auth.models import User


LEGAL_STATUSES = [
    ('ip', 'ИП'),
    ('self_employed', 'Самозанятый'),
    ('individual', 'Физическое лицо'),
]

CALL_STATUSES = [
    ('negotiation', 'Согласование'),
    ('tz_creation', 'Создание ТЗ'),
    ('tz_approval', 'Согласование ТЗ'),
    ('contract_signing', 'Подписание договора'),
    ('in_progress', 'В работе'),
    ('completed', 'Выполнено'),
    ('refusal', 'Отказ'),
    ('call_back', 'Перезвонить'),
    ('unavailable', 'Не доступен'),
]


class Client(models.Model):
    industry = models.CharField('Сфера деятельности', max_length=200, blank=True)
    city = models.CharField('Город', max_length=200, blank=True)
    company_name = models.CharField('Наименование', max_length=300, blank=True)
    name = models.CharField('Имя', max_length=200, blank=True)
    phone = models.CharField('Телефон', max_length=200)
    legal_status = models.CharField('Правовой статус', max_length=20, choices=LEGAL_STATUSES, blank=True)
    online_booking = models.CharField('Онлайн-запись', max_length=5000, blank=True)
    website_link = models.CharField('Ссылка на сайт', max_length=5000, blank=True)
    map_link = models.CharField('Ссылка на Яндекс/2ГИС', max_length=5000, blank=True)
    comment = models.TextField('Комментарий', blank=True)
    assigned_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='clients', verbose_name='Ответственный менеджер')
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='imported_clients', verbose_name='Подгрузил')
    is_archived = models.BooleanField('В архиве', default=False)
    is_deleted = models.BooleanField('Удалён', default=False)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Клиент'
        verbose_name_plural = 'База клиентов'

    def __str__(self):
        return self.name or self.company_name or self.phone


class Call(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='calls', verbose_name='Клиент')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls', verbose_name='Менеджер')
    script = models.TextField('Скрипт', blank=True)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=30, choices=CALL_STATUSES, default='in_progress')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Обзвон'
        verbose_name_plural = 'Обзвоны'

    def __str__(self):
        return f'{self.client} — {self.get_status_display()}'


class ClientDocument(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents', verbose_name='Клиент')
    title = models.CharField('Название', max_length=300)
    file = models.FileField('Файл', upload_to='client_documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Загрузил')
    created_at = models.DateTimeField('Загружен', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Документ клиента'
        verbose_name_plural = 'Документы клиентов'

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return self.file.name.split('/')[-1] if self.file else ''

    @property
    def extension(self):
        return self.filename.rsplit('.', 1)[-1].upper() if '.' in self.filename else ''


ACTIVITY_TYPES = [
    ('status', 'Смена статуса'),
    ('edit', 'Редактирование'),
    ('comment', 'Комментарий'),
    ('document', 'Документ'),
    ('call', 'Обзвон'),
]


class ClientActivity(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='activities', verbose_name='Клиент')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Пользователь')
    activity_type = models.CharField('Тип', max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField('Заголовок', max_length=300)
    detail = models.TextField('Детали', blank=True)
    old_value = models.CharField('Было', max_length=500, blank=True)
    new_value = models.CharField('Стало', max_length=500, blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Активность клиента'
        verbose_name_plural = 'Активность клиентов'

    def __str__(self):
        return f'{self.get_activity_type_display()}: {self.title}'
