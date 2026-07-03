from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('products/', views.products, name='products'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/<int:pk>/', views.goods_detail, name='goods_detail'),
    path('profile/', views.profile, name='profile'),
]
