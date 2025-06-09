from django.urls import path
from .views import farmer_login
from .views import farmer_register
from .views import update_farmer
from django.urls import path
from .views import create_transport_request
from .views import detect_disease
from .views import download_diagnosis_pdf
from .views import market_insights
from .views import voice_command
from .views import farmer_profile

urlpatterns = [
    path('login/', farmer_login),
    path('register/', farmer_register),
    path('farmers/<int:pk>/', update_farmer),
    path('transport-requests/', create_transport_request, name='create_transport_request'),
    path('detect_disease/', detect_disease),
    path('download-diagnosis-pdf/', download_diagnosis_pdf),
    path('market_insights/', market_insights),
    path('voice_command/', voice_command),
   # path('farmer-profile/<int:pk>/', farmer_profile),
    path('farmer-profile/<int:farmer_id>/', farmer_profile),




]


