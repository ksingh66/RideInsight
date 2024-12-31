"""
URL configuration for chatbot_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from chat_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='chat_app/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('', views.upload_view, name='upload'),  # Changed from 'upload/' to '' to make it the main page
    # Chat view (after file upload)
    path('chat/<int:id>/', views.chat_view, name='chat'),
    # End chat endpoint
    path('end-chat/<int:id>/', views.end_chat, name='end_chat'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
