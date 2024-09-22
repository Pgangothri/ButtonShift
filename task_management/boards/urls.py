from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkBoardViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'workboards', WorkBoardViewSet, basename='workboard')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),  # Expose API under '/api/' URL
    path('api/auth/', include('rest_framework.urls')),  # Optional: add if you're using DRF's login view
]
