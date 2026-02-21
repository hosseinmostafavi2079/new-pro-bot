from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from events.views import (
    EventViewSet, 
    LecturerViewSet, 
    CategoryViewSet, 
    MyTicketsView, 
    AdminStatsView,
    AdminUserViewSet
)
from core.views import RegisterView, CustomTokenObtainPairView, SystemSettingView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from payments.views import PurchaseTicketView

# ساخت روتر خودکار برای APIها
router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'lecturers', LecturerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'admin/users', AdminUserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/payments/', include('payments.urls')),
    
    # مسیرهای لاگین و تنظیمات (بروزرسانی شده)
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='auth_register'),
    path('api/settings/', SystemSettingView.as_view(), name='system_settings'),
    
    path('api/purchase/', PurchaseTicketView.as_view(), name='purchase_ticket'),
    path('api/my-tickets/', MyTicketsView.as_view(), name='my_tickets'),
    path('api/admin/stats/', AdminStatsView.as_view(), name='admin_stats'),
]

# --- این قسمت حیاتی است: اضافه کردن مسیر فایل‌های مدیا ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)