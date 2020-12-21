from django.db import models
from django.contrib.auth.models import User#auth_user表 id/ username/ password/ email/等 用户保存在这
from PIL import Image

class Profile(models.Model):#users_profile表 id/ user_id/ image/
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    @property#把定义的函数变成属性被实例调用 好好回想下多少表怎么建立的对应关系
    def followers(self):
        return Follow.objects.filter(follow_user=self.user).count()

    @property
    def following(self):
        return Follow.objects.filter(user=self.user).count()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):#缩略保存头像 但是还弄倒了 可删除
        super().save()#父类 就是model.save 保存
        img = Image.open(self.image.path)#PIL的image
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class Follow(models.Model):#user_follow表 id/ date/ follow_user_id/ user_id/
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    follow_user = models.ForeignKey(User, related_name='follow_user', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
