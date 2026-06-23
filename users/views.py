from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone

from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import UserProfile, UserProduct, ProductFile, UserSetting, Goods, GoodsFile, UserGoods
from main.models import Product


def register(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    form = UserRegistrationForm()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('users:dashboard')
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    form = UserLoginForm()
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'users:dashboard')
            return redirect(next_url)
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/account/login/')
def dashboard(request):
    user = request.user
    settings = UserSetting.objects.filter(is_active=True)
    active_goods = UserGoods.objects.filter(user=user, is_active=True).select_related('goods')

    return render(request, 'users/dashboard.html', {
        'title': 'Мой кабинет',
        'active_goods': active_goods,
        'settings': settings,
        'user': user,
    })


@login_required(login_url='/account/login/')
def products(request):
    user = request.user
    user_products = UserProduct.objects.filter(user=user, is_active=True).select_related('product')

    return render(request, 'users/product_list.html', {
        'title': 'Мои товары',
        'user_products': user_products,
        'now': timezone.now(),
    })


@login_required(login_url='/account/login/')
def product_detail(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)

    access = UserProduct.objects.filter(user=user, product=product, is_active=True).first()
    if not access:
        messages.error(request, 'У вас нет доступа к этому товару')
        return redirect('users:products')

    files = ProductFile.objects.filter(product=product)

    return render(request, 'users/product_detail.html', {
        'title': product.title,
        'product': product,
        'files': files,
        'access': access,
    })



@login_required(login_url='/account/login/')
def goods_list(request):
    user = request.user
    user_goods = UserGoods.objects.filter(user=user, is_active=True).select_related('goods')

    return render(request, 'users/goods_list.html', {
        'title': 'Мои товары',
        'user_goods': user_goods,
        'now': timezone.now(),
    })


@login_required(login_url='/account/login/')
def goods_detail(request, pk):
    user = request.user
    goods = get_object_or_404(Goods, pk=pk)

    access = UserGoods.objects.filter(user=user, goods=goods, is_active=True).first()
    if not access:
        messages.error(request, 'У вас нет доступа к этому товару')
        return redirect('users:goods_list')

    files = GoodsFile.objects.filter(goods=goods)

    return render(request, 'users/goods_detail.html', {
        'title': goods.title,
        'goods': goods,
        'files': files,
        'access': access,
    })


@login_required(login_url='/account/login/')
def profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён')

        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        new_password2 = request.POST.get('new_password2', '')
        if old_password and new_password:
            if not user.check_password(old_password):
                messages.error(request, 'Неверный текущий пароль')
            elif new_password != new_password2:
                messages.error(request, 'Пароли не совпадают')
            elif len(new_password) < 8:
                messages.error(request, 'Пароль должен быть не менее 8 символов')
            else:
                user.set_password(new_password)
                user.save()
                login(request, user)
                messages.success(request, 'Пароль успешно изменён')

        return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'users/profile.html', {
        'title': 'Мой профиль',
        'form': form,
        'profile': profile,
    })
