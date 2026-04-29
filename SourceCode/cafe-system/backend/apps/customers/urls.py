from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

# TODO: Register viewsets with router
# router.register(r'endpoint', ViewSet)

app_name = 'customers'

urlpatterns = [
    path('', include(router.urls)),
]
