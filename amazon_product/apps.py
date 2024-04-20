from django.apps import AppConfig


class AmazonProductConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'amazon_product'

    def ready(self):
        # Import the background task and start it
        from .task import my_job
        my_job()

