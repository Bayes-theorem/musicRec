from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import date

# Create your views here.

@login_required(login_url='user:login')
def detail_view(request):
    song_id=request.GET.get('id')
    #将song_id存入seesion,后续评分和评论需要用到
    request.session["song_id"]=song_id #写入session(也写入浏览器cookie中)
    #获取歌曲详情
    songInfo=Song.objects.get(song_id=song_id) 
    #print('songInfo',songInfo)
    #获取对应的歌手信息（可能有多个歌手）
    singers=songInfo.singer.all()
    #print('singers',singers)
    #获取评论信息
    current_song = Song.objects.get(pk=request.session.get('song_id'))
    current_user = User.objects.get(username=request.session.get('info'))
    comments=Comment.objects.filter(song=current_song).order_by('-comment_date')
    return render(request,'play/detail.html',{"songInfo":songInfo,'singers':singers,'comments':comments})

def rating(request):
    if request.method == 'GET':
        current_song = Song.objects.get(pk=request.session.get('song_id'))
        current_user = User.objects.get(username=request.session.get('info'))
        rating=Rating.objects.filter(song=current_song,rating_user=current_user)
        if(len(rating)==0):
            rating_number=0
        else:
            rating_number=rating[0].rating_number
        return JsonResponse({"msg": "查询成功", "rating_number":rating_number,"success": True})
    if request.method == 'POST':
        current_song = Song.objects.get(pk=request.session.get('song_id'))
        current_user = User.objects.get(username=request.session.get('info'))
        rating_number =request.POST.get("rating_number")
        Rating.objects.update_or_create(
            song=current_song,
            rating_user=current_user,
            defaults={'rating_number': rating_number,'rating_date':date.today()}
        )
        return JsonResponse({"msg": "评分成功", "success": True})
        
def comment(request):
    current_song = Song.objects.get(pk=request.session.get('song_id'))
    current_user = User.objects.get(username=request.session.get('info'))
    comment_text =request.POST.get("comment_text")
    Comment.objects.create(
            song=current_song,
            comment_user=current_user,
            comment_text=comment_text,
            comment_date=date.today()
        )
    return JsonResponse({"msg": "评论发布成功", "success": True})


