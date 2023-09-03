from django.shortcuts import render
from django.contrib.auth.decorators import login_required
#数据分析
import numpy as np
import pandas as pd
import math
import random
#分页
from django.core.paginator import Paginator , PageNotAnInteger,EmptyPage

from play.models import *

# Create your views here.
@login_required(login_url='user:login')
def recommendation_view(request):

    ratings=Rating.objects.all()

    #数据准备
    users=dict()
    all_items=set()
    for rating in ratings:
        all_items.add(rating.song.song_name)
        if(rating.rating_user.username in users.keys()):
            users[rating.rating_user.username][rating.song.song_name]=rating.rating_number
        else:
            users[rating.rating_user.username]=dict()
            users[rating.rating_user.username][rating.song.song_name]=rating.rating_number
    ##print(users)

    ##print('当前用户',request.session.get('info'))

    current_user=request.session.get('info')
    rated_items=set([key for key in users[current_user].keys() if users[current_user][key] > 0])
    unrated_items=list(all_items.__sub__(rated_items))
    ##print(unrated_items)

    #基于用户相似度的协同过滤推荐
    userCF_result=userCF(users,unrated_items,current_user)
    FM_BiasSVD_result=FM_BiasSVD(users,unrated_items,current_user)
    ##print('基于用户相似度的协同过滤推荐结果'，userCF_result)
    ##print('基于矩阵分解的协同过滤推荐结果',FM_BiasSVD_result)

    userCF_songs=Song.objects.filter(song_name__in=list(userCF_result))
    FM_BiasSVD_songs=Song.objects.filter(song_name__in=list(FM_BiasSVD_result))

    # print('userCF_songs',userCF_songs)
    # print('FM_BiasSVD_songs',FM_BiasSVD_songs)

    #分页
    userCF_paginator = Paginator(userCF_songs,6)
    try:
    # GET请求方式，get()获取指定Key值所对应的value值
    # 获取index的值，如果没有，则设置使用默认值1
        userCF_number = request.GET.get('userCF_number','1')
    # 获取第几页
        userCF_page = userCF_paginator.page(userCF_number)
    except PageNotAnInteger:
    # 如果输入的页码数不是整数，那么显示第一页数据
        userCF_page = userCF_paginator.page(1)
    except EmptyPage:
        userCF_page = userCF_paginator.page(userCF_paginator.num_pages)

    FM_BiasSVD_paginator = Paginator(FM_BiasSVD_songs,6)
    try:
    # GET请求方式，get()获取指定Key值所对应的value值
    # 获取index的值，如果没有，则设置使用默认值1
        FM_BiasSVD_number = request.GET.get('FM_BiasSVD_number','1')
    # 获取第几页
        FM_BiasSVD_page = FM_BiasSVD_paginator.page(FM_BiasSVD_number)
    except PageNotAnInteger:
    # 如果输入的页码数不是整数，那么显示第一页数据
        FM_BiasSVD_page = FM_BiasSVD_paginator.page(1)
    except EmptyPage:
        FM_BiasSVD_page = FM_BiasSVD_paginator.page(FM_BiasSVD_paginator.num_pages)
    

    return render(request,'play/recommend.html',{'userCF_page':userCF_page,'userCF_paginator':userCF_paginator,'FM_BiasSVD_page':FM_BiasSVD_page,'FM_BiasSVD_paginator':FM_BiasSVD_paginator})

#基于用户相似度的协同过滤推荐
def userCF(users,unrated_items,current_user):
    user_data = users
    ##用户相似度矩阵
    similarity_matrix = pd.DataFrame(
        np.identity(len(user_data)),
        index=user_data.keys(),
        columns=user_data.keys(),)
    for u in user_data.keys():
        for v in user_data.keys():
            if u == v:
                continue
            u_set = set( [key for key in user_data[u].keys() if user_data[u][key] > 0])
            v_set = set( [key for key in user_data[v].keys() if user_data[v][key] > 0])
            similarity_matrix[u][v] = float(len(u_set & v_set)) / math.sqrt(len(u_set) * len(v_set))
    ###print('*************相似度矩阵*****************')
    ###print(similarity_matrix)
    ##当前登录的用户
    target_user = current_user
    num = 2
    # 由于最相似的用户为自己，去除本身
    sim_users = similarity_matrix[target_user].sort_values(ascending=False)[1:num+1].index.tolist()
    ##预测当前用户对未评分的item的评分
    target_item_list = unrated_items
    target_rating_list = []
    for target_item in target_item_list:
        weighted_scores = 0.
        weighted_sum = 0.
        for user in sim_users:
            u_set=set( [key for key in user_data[user].keys() if user_data[user][key] > 0])
            if(target_item not in u_set):
                user_data[user][target_item]=0
            weighted_scores += similarity_matrix[target_user][user] * user_data[user][target_item] 
            weighted_sum += similarity_matrix[target_user][user]
        target_item_pred = weighted_scores / weighted_sum
        target_rating_list.append(target_item_pred)
    ###print('*************预测评分*****************')
    ###print(target_rating_list)
    ##将结果降序排序，并返回
    sorted_target_rating_list, sorted_target_item_list = zip(*sorted(zip(target_rating_list, target_item_list),reverse=True))
    return sorted_target_item_list

#基于矩阵分解的协同过滤推荐

class BiasSVD():
    def __init__(self, rating_data, F=5, alpha=0.1, lmbda=0.1, max_iter=100):
        self.F = F          # 这个表示隐向量的维度
        self.P = dict()     # 用户矩阵P  大小是[users_num, F]
        self.Q = dict()     # 物品矩阵Q  大小是[item_nums, F]
        self.bu = dict()    # 用户偏置系数
        self.bi = dict()    # 物品偏置系数
        self.mu = 0         # 全局偏置系数
        self.alpha = alpha  # 学习率
        self.lmbda = lmbda  # 正则项系数
        self.max_iter = max_iter        # 最大迭代次数
        self.rating_data = rating_data  # 评分矩阵

        for user, items in self.rating_data.items():
            # 初始化矩阵P和Q, 随机数需要和1/sqrt(F)成正比
            self.P[user] = [random.random() / math.sqrt(self.F) for x in range(0, F)]
            self.bu[user] = 0
            for item, rating in items.items():
                if item not in self.Q:
                    self.Q[item] = [random.random() / math.sqrt(self.F) for x in range(0, F)]
                    self.bi[item] = 0

    # 采用随机梯度下降的方式训练模型参数
    def train(self):
        cnt, mu_sum = 0, 0
        for user, items in self.rating_data.items():
            for item, rui in items.items():
                mu_sum, cnt = mu_sum + rui, cnt + 1
        self.mu = mu_sum / cnt

        for step in range(self.max_iter):
            # 遍历所有的用户及历史交互物品
            for user, items in self.rating_data.items():
                # 遍历历史交互物品
                for item, rui in items.items():
                    rhat_ui = self.predict(user, item)  # 评分预测
                    e_ui = rui - rhat_ui  				# 评分预测偏差

                    # 参数更新
                    self.bu[user] += self.alpha * (e_ui - self.lmbda * self.bu[user])
                    self.bi[item] += self.alpha * (e_ui - self.lmbda * self.bi[item])
                    for k in range(0, self.F):
                        self.P[user][k] += self.alpha * (e_ui * self.Q[item][k] - self.lmbda * self.P[user][k])
                        self.Q[item][k] += self.alpha * (e_ui * self.P[user][k] - self.lmbda * self.Q[item][k])
            # 逐步降低学习率
            self.alpha *= 0.1


    # 评分预测
    def predict(self, user, item):
        return sum(self.P[user][f] * self.Q[item][f] for f in range(0, self.F)) + self.bu[user] + self.bi[item] + self.mu
    

def FM_BiasSVD(users,unrated_items,current_user):
    rating_data = users
    # 建立模型
    basicsvd = BiasSVD(rating_data, F=3)
    # 参数训练
    basicsvd.train()
    # 预测用户对item的评分
    target_item_list = unrated_items
    target_rating_list = []
    for item in target_item_list:
        target_rating_list.append(basicsvd.predict(current_user, item))
    
    ##将结果降序排序，并返回
    sorted_target_rating_list, sorted_target_item_list = zip(*sorted(zip(target_rating_list, target_item_list),reverse=True))
    return sorted_target_item_list
