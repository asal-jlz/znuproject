"""
URL configuration for uni_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from core.views import home
from django.conf import settings
from django.conf.urls.static import static
from core.views import home, conference_detail, upload_article
from core import views
from django.contrib.auth import views as auth_views
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), 
    path('', views.home, name='home'),
    path('scientific-committee/', views.scientific_committee, name='scientific_committee'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('conference/<int:pk>/', views.conference_detail, name='conference_detail'),
    path('upload/', views.upload_article, name='upload_article'),
    path('update-status/<int:article_id>/<str:new_status>/', views.update_article_status, name='update_status'),
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('professor/<int:pk>/', views.professor_profile, name='professor_profile'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('search/', views.global_search, name='global_search'),
    path('ai-assistant/', views.ai_assistant_api, name='ai_assistant'),
    path('upload-receipt/<int:article_id>/', views.upload_receipt, name='upload_receipt'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
