from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("",views.index_view,name="index"),
    
    path("play/",include("play.urls")),
    path("user/",include("user.urls")),
    path("recommend/",include("recommend.urls")),
]
