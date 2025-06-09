
from django.contrib import admin
from django.urls import path
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('farmers.urls')),
   # path('api/', include('transport.urls')),



]


