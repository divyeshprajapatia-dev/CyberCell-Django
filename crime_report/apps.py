from django.apps import AppConfig

class CrimeReportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crime_report'

    def ready(self):
        import crime_report.signals