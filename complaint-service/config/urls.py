from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from complaint import views

router = DefaultRouter()
router.register(r'complaints', views.ComplaintView)
router.register(r'reviews', views.ComplaintReviewView)
router.register(r'transactions', views.TransactionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # 可以添加自定义路径

]