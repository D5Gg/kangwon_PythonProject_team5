# index/apps.py

from django.apps import AppConfig

class IndexConfig(AppConfig):  # 기존 NotesConfig -> IndexConfig
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'index'
