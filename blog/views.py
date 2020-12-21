from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Comment, Preference
from users.models import Follow, Profile
import sys
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .forms import NewCommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http.response import JsonResponse

def is_users(post_user, logged_user):
    return post_user == logged_user

PAGINATION_COUNT = 3

class PostListView(LoginRequiredMixin, ListView):
    model = Post#model
    template_name = 'blog/home.html'#模板用template_name
    context_object_name = 'posts'#传入模板的字典名
    ordering = ['-date_posted']#排序
    paginate_by = PAGINATION_COUNT#page 定义属性 其他return render自动处理 这5行属性直接显示主要页面内容

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)#调用父类ListView的get_context_data方法
        all_users = []
        data_counter = Post.objects.values('author').annotate(author_count=Count('author')).order_by('-author_count')[:6]
        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())
        data['preference'] = Preference.objects.all()
        data['all_users'] = all_users
        print(all_users)
        return data

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')


class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATION_COUNT

    def visible_user(self):#用这个限定 否则返回所有post
        return get_object_or_404(User, username=self.kwargs.get('username'))#User是要查询的model,后面的是查询条件

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == '', file=sys.stderr)

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (Follow.objects.filter(user=logged_user,
                                                follow_user=visible_user).count() == 0)
        data = super().get_context_data(**kwargs)

        data['user_profile'] = visible_user
        data['can_follow'] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):#post方式接收follow unfollow
        if request.user.id is not None:
            follows_between = Follow.objects.filter(user=request.user, follow_user=self.visible_user())
            if 'follow' in request.POST:
                new_relation = Follow(user=request.user, follow_user=self.visible_user())
                if follows_between.count() == 0:
                    new_relation.save()
            elif 'unfollow' in request.POST:
                if follows_between.count() > 0:
                    follows_between.delete()
        return self.get(self, request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):#查询关联的评论post_connected是外键
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):#添加评论
        new_comment = Comment(content=request.POST.get('content'),#创建方法
                              author=self.request.user,
                              post_connected=self.get_object())#和哪个post关联
        new_comment.save()
        return self.get(self, request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    context_object_name = 'post'
    success_url = '/'#Deleteview CreateView UpdateView 有这个选项

    def test_func(self):#校验用户
        return is_users(self.get_object().author, self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):#继承CreateView 模板就用个{{ form | crispy }} 特别智能
    model = Post#表
    fields = ['content']#列
    template_name = 'blog/post_new.html'
    success_url = '/'#Deleteview CreateView UpdateView 有这个选项

    def form_valid(self, form):#把当前用户设为author 再去校验 其他列的值都设定了默认 date_posted likes
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Add a new post'#增加字典内容传递给模板
        return data


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):#继承UserPassesTestMixin 定义test_func校验
    model = Post
    fields = ['content']
    template_name = 'blog/post_new.html'
    success_url = '/'#Deleteview CreateView UpdateView 有这个选项

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Edit a post'
        return data


class FollowsListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):#拿到用户
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):#根据用户去查
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):#返回数据
        data = super().get_context_data(**kwargs)
        data['follow'] = 'follows'#模板用这个判断
        return data


class FollowersListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'#模板用这个判断
        return data


# Like Functionality====================================================================================

@login_required
def postpreference(request, postid, userpreference):#
        if request.method == "POST":
                eachpost= get_object_or_404(Post, id=postid)
                obj=''
                valueobj=''
                try:
                        obj= Preference.objects.get(user= request.user, post= eachpost)
                        valueobj= obj.value #value of userpreference
                        valueobj= int(valueobj)
                        userpreference= int(userpreference)
                        if valueobj != userpreference:
                                obj.delete()
                                upref= Preference()
                                upref.user= request.user
                                upref.post= eachpost
                                upref.value= userpreference

                                if userpreference == 1 and valueobj != 1:
                                        eachpost.likes += 1
                                        eachpost.dislikes -=1
                                elif userpreference == 2 and valueobj != 2:
                                        eachpost.dislikes += 1
                                        eachpost.likes -= 1

                                upref.save()
                                eachpost.save()
                                context= {'eachpost': eachpost,
                                  'postid': postid}
                                return redirect('blog-home')

                        elif valueobj == userpreference:
                                obj.delete()
                                if userpreference == 1:
                                        eachpost.likes -= 1
                                elif userpreference == 2:
                                        eachpost.dislikes -= 1
                                eachpost.save()
                                context= {'eachpost': eachpost,
                                  'postid': postid}
                                return redirect('blog-home')

                except Preference.DoesNotExist:
                        upref= Preference()
                        upref.user= request.user
                        upref.post= eachpost
                        upref.value= userpreference
                        userpreference= int(userpreference)
                        if userpreference == 1:
                                eachpost.likes += 1
                        elif userpreference == 2:
                                eachpost.dislikes +=1
                        upref.save()
                        eachpost.save()
                        context= {'eachpost': eachpost,
                          'postid': postid}
                        return redirect('blog-home')
        else:
                eachpost= get_object_or_404(Post, id=postid)
                context= {'eachpost': eachpost,
                          'postid': postid}
                return redirect('blog-home')



def about(request):
    return render(request,'blog/about.html',)



