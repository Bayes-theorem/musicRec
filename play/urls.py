from django.urls import path

from . import views
app_name='play'

urlpatterns = [
    path('detail/', views.detail_view,name='detail'), 
    path('rating/', views.rating,name='rating'),
    path('comment/', views.comment,name='comment'),
]