from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# app.py中   def ready(self):#使用了signal        import users.signals
# signal that gets fired after the user is saved
@receiver(post_save, sender=User)#User表改动后 执行下面函数
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
