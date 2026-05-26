from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from ingestion.views import UploadView
from review.views import EmissionRecordViewSet, DashboardSummaryView

router = DefaultRouter()
router.register(r'records', EmissionRecordViewSet, basename='record')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/upload/', UploadView.as_view(), name='upload'),
    path('api/dashboard/', DashboardSummaryView.as_view(), name='dashboard'),
    path('api/auth/login/', obtain_auth_token, name='login'),
]