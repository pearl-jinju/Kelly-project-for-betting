"""
URL configuration for kelly project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main.views import MainPage, AutoBet ,Save_Recent_Data,Save_All_Data, DBsearch,Pick

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainPage.as_view()),
    path('autobet', AutoBet.as_view()),
    path('save_data', Save_Recent_Data.as_view()),
    path('save_all_data', Save_All_Data.as_view()),
    path('dbsearch', DBsearch.as_view()),
    path('pick', Pick.as_view()),
]
