from django.http import HttpResponse
from django.shortcuts import render
from play.models import *


def index_view(request):
    
    monthlyTopSongList=Song.objects.all()[:10]
    dailyTopSongList=Song.objects.all()[:3]

    return render(request,'index.html',locals()) #返回当前位置的全部局部变量