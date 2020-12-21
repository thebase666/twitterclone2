from django.shortcuts import render, redirect
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():#通过校验没有报错 form就有form.cleaned_data
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}.')#messages.success直接就给模板传递messages了
            return redirect('login')#base中 {% if messages %} f'{变量}' 有f把变量替换 如果没有f显示Account created for {username}.
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=request.user)#显示调用替换处理当前用户的数据内容
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, f'Account has been updated.')
            return redirect('profile')
    else:
        uform = UserUpdateForm(instance=request.user)#显示调用替换处理当前用户的数据内容
        pform = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'uform': uform, 'pform': pform})

@login_required
def SearchView(request):
    if request.method == 'POST':
        kerko = request.POST.get('search')#html中  <input required name="search"
        #print(kerko)
        results = User.objects.filter(username__contains=kerko)
        context = {
            'results': results
        }
        return render(request, 'users/search_result.html', context)
