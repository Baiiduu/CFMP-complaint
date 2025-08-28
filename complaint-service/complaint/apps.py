from django.apps import AppConfig

class ComplaintConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'complaint'

    def ready(self):
        """
        应用启动时执行的初始化代码
        """
        from config.nacos_heartbeat import start_nacos_heartbeat
        start_nacos_heartbeat()
        # 如果需要在应用启动时执行定时任务或其他初始化操作，可以在这里添加
        # 例如：
        # from . import schedulers
        # schedulers.start_scheduler()

