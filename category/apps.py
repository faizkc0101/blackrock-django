
from django.apps import AppConfig

class CategoryConfig(AppConfig):  # Corrected class name
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'category'  # Ensure this matches your app directory name
