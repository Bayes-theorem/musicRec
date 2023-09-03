from django.shortcuts import render,redirect
##表单
from django import forms 
##CBV基于类的视图
from django.views import View
##django自带的User和Group模型
from django.contrib.auth.models import User,Group
##登录验证
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from play.models import *

##登录表单
class LoginForm(forms.Form):
    name=forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class":"form-control","placeholder":"用户名"}),
        required=True
    )
    password=forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"密码"}),
        required=True
    )
      
class LoginView(View):
   
    def get(self,request):
        """
        显示登录页面
        """
        return render(request,'user/login.html',{'form':LoginForm()}) # 渲染模板

    def post(self,request):
        """
        提交登录页面表单
        """
        form = LoginForm(request.POST) # 接收Form表单
        # 验证表单
        if form.is_valid():
           name = request.POST['name'] 
           password = request.POST['password']  
           user = authenticate(request, username=name, password=password)  # 授权校验
        #    user_object= models.Userinfo.objects.filter(**form.cleaned_data).first()
           if user is None:
               form.add_error("password","用户名或密码错误")
           else:
               key=list(User.objects.filter(username=name).values("groups"))[0]["groups"]
               group = list(Group.objects.filter(id=key).values("name"))[0]["name"]  
               login(request,user)
               request.session["info"]=user.username #写入session(也写入浏览器cookie中)
               request.session["group"]=group #写入session(也写入浏览器cookie中)  
               return redirect("/")
        return render(request,"user/login.html",{"form":form})

def to_logout(request):
    logout(request)	# 清除response的cookie和django_session中记录
    return redirect('/user/login/')

@login_required(login_url='user:login')
def analysis(request):
    current_user = User.objects.get(username=request.session.get('info'))
    songs=Song.objects.filter(singer=current_user)
    print('songs',songs)
    song_dynamics=Dynamic.objects.filter(song__in=songs)
    print('song_dynamic',song_dynamics)

    song_data=dict()
    for i in range(len(song_dynamics)):
        song_data[songs[i].song_name]=[]
        song_data[songs[i].song_name].append(song_dynamics[i].dynamic_plays)
        song_data[songs[i].song_name].append(song_dynamics[i].dynamic_search)
        song_data[songs[i].song_name].append(song_dynamics[i].dynamic_down)
    return render(request,'user/analysis.html',{'song_data':song_data})