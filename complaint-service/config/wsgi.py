# config/wsgi.py
"""
WSGI config for complaint service project.

It exposes the WSGI callable as a module-level variable named `[application](file://E:\大三上\软工\小学期\CFMP\后端\cfmp\config\asgi.py#L19-L27)`.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# 设置默认的 Django 配置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 获取 WSGI 应用实例
application = get_wsgi_application()