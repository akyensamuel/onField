from django.apps import AppConfig


class DataformConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DataForm'
    
    def ready(self):
        """Import signals when the app is ready"""
        import DataForm.signals
