from django.urls import path
from .views import profile_view
#from .views import register_view, login_view

urlpatterns = [
    # path('login/', login_view, name='login'),
    # path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
]
