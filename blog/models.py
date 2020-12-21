from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):#blog_post表 author_id/
    content = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)#多行post的author是一个用户 author_id对应user表的id
    likes = models.IntegerField(default=0)#多行post的like是一个用户 一个post被多个用户like ManyToMany 新建表id/ post_id/ user_id/ 每一个赞都是一条数据
    dislikes = models.IntegerField(default=0)

    def __str__(self):
        return self.content[:5]

    @property#把定义的函数变成属性被实例调用 好好回想下多少表怎么建立的对应关系
    def number_of_comments(self):
        return Comment.objects.filter(post_connected=self).count()

class Comment(models.Model):#blog_comment表 author_id/ post_connected_id/
    content = models.TextField(max_length=150)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_connected = models.ForeignKey(Post, on_delete=models.CASCADE)

class Preference(models.Model):#blog_preference表
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.IntegerField()
    date = models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.user) + ':' + str(self.post) +':' + str(self.value)

    class Meta:
       unique_together = ("user", "post", "value")#一旦三者都相同，则会被Django拒绝创建
