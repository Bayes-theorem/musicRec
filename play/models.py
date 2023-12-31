from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# 歌曲分类表
class Label(models.Model):
    label_id = models.AutoField('序号', primary_key=True)
    label_name = models.CharField('分类标签', max_length=10)

    def __str__(self):
        return self.label_name

    class Meta:
        verbose_name = '歌曲分类'
        verbose_name_plural = '歌曲分类'


# 歌曲信息表
class Song(models.Model):
    song_id = models.AutoField('序号', primary_key=True)
    song_name = models.CharField('歌名', max_length=50)
    song_time = models.CharField('时长', max_length=10)
    song_album = models.CharField('专辑', max_length=50)
    song_languages = models.CharField('语种', max_length=20)
    song_release = models.DateField('发行时间', max_length=20)
    song_img = models.CharField('歌曲图片', max_length=100)
    song_lyrics = models.CharField('歌词', max_length=500, default='暂无歌词')
    song_file = models.CharField('歌曲文件', max_length=100)
    label = models.ForeignKey(Label, on_delete=models.CASCADE,verbose_name='类型')
    singer = models.ManyToManyField(User, verbose_name='歌手') #多对多

    def __str__(self):
        return self.song_name

    class Meta:
        verbose_name = '歌曲信息'
        verbose_name_plural = '歌曲信息'


# 歌曲动态表
class Dynamic(models.Model):
    dynamic_id = models.AutoField('序号', primary_key=True)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name='歌名')
    dynamic_plays = models.IntegerField('播放次数')
    dynamic_search = models.IntegerField('搜索次数')
    dynamic_down = models.IntegerField('下载次数')

    class Meta:
        verbose_name = '歌曲动态'
        verbose_name_plural = '歌曲动态'


# 歌曲评论表
class Comment(models.Model):
    comment_id = models.AutoField('序号', primary_key=True)
    comment_text = models.CharField('内容', max_length=500)
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name='歌名')
    comment_date = models.DateField('日期', max_length=50)

    class Meta:
        verbose_name = '歌曲评论'
        verbose_name_plural = '歌曲评论'


# 歌曲评分表
class Rating(models.Model):
    rating_id = models.AutoField('序号', primary_key=True)
    rating_number = models.IntegerField('评分')
    rating_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name='歌名')
    rating_date = models.DateField('日期', max_length=50)

    class Meta:
        verbose_name = '歌曲评分'
        verbose_name_plural = '歌曲评分'

