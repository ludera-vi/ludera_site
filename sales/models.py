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
        indexes = [
            models.Index(fields=['is_archived', 'is_deleted']),
            models.Index(fields=['assigned_manager']),
            models.Index(fields=['phone']),
        ]

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
        indexes = [
            models.Index(fields=['client', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['manager', 'created_at']),
        ]

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


class Board(models.Model):
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'

    def __str__(self):
        return self.title


class Column(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='columns', verbose_name='Доска')
    title = models.CharField('Название', max_length=255)
    position = models.PositiveIntegerField('Порядок', default=0)
    is_collapsed = models.BooleanField('Свёрнута', default=False)

    class Meta:
        ordering = ['position']
        verbose_name = 'Колонка'
        verbose_name_plural = 'Колонки'

    def __str__(self):
        return f'{self.board.title} — {self.title}'


class Card(models.Model):
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name='cards', verbose_name='Колонка')
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Клиент')
    responsible = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='kanban_cards', verbose_name='Ответственный')
    parent_card = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Родительская карточка')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_cards', verbose_name='Создал')
    position = models.PositiveIntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлена', auto_now=True)

    class Meta:
        ordering = ['position']
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'

    def __str__(self):
        return self.title


CHAT_TYPES = [
    ('personal', 'Личный'),
    ('group', 'Групповой'),
    ('client', 'По клиенту'),
    ('card', 'По карточке'),
]


class Chat(models.Model):
    title = models.CharField('Название', max_length=255, blank=True)
    chat_type = models.CharField('Тип', max_length=20, choices=CHAT_TYPES)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True, related_name='chats', verbose_name='Карточка')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='chats', verbose_name='Клиент')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    is_deleted = models.BooleanField('Удалён', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'

    def __str__(self):
        return self.title or f'{self.get_chat_type_display()} #{self.pk}'


class ChatMember(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='members', verbose_name='Чат')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    last_read_at = models.DateTimeField('Последнее прочтение', null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_members', verbose_name='Добавил')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        unique_together = ['chat', 'user']
        verbose_name = 'Участник чата'
        verbose_name_plural = 'Участники чата'

    def __str__(self):
        return f'{self.user} в {self.chat}'


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name='Чат')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Автор')
    message = models.TextField('Сообщение')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return f'{self.author}: {self.message[:50]}'


class InfoTopic(models.Model):
    title = models.CharField('Заголовок', max_length=300)
    content = models.TextField('Содержание', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Создал')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Топик информации'
        verbose_name_plural = 'Информация'

    def __str__(self):
        return self.title


class InfoTopicRead(models.Model):
    topic = models.ForeignKey(InfoTopic, on_delete=models.CASCADE, related_name='reads', verbose_name='Топик')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    read_at = models.DateTimeField('Прочитано', auto_now_add=True)

    class Meta:
        unique_together = ['topic', 'user']
        verbose_name = 'Прочтение топика'
        verbose_name_plural = 'Прочтения топиков'

    def __str__(self):
        return f'{self.user} прочитал {self.topic}'
