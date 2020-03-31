from django.urls import path
from .views import home_view, search_view

urlpatterns = [
    path('', home_view, name="home"),
    path('account_tweet_analysis', search_view, name="analysis"),
]