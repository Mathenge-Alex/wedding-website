from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from images import views

urlpatterns = [
    path('gallery/', views.gallery, name='gallery'),
    path('', views.home, name='home'),
    path('image/<int:pk>/', views.image_detail, name='image_detail'),
    path('contact/', views.contact, name='contact'),
    path('about-artist/', views.about_artist, name='about_artist'),
    path('pricing/', views.pricing, name='pricing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
