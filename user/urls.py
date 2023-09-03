from django.urls import path

from . import views
app_name='user'

urlpatterns = [
    path('login/',views.LoginView.as_view(),name="login"),
    path('logout/',views.to_logout, name="logout"),

    path('analysis/',views.analysis,name='analysis')
]