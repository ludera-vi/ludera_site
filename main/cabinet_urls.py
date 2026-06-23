from django.urls import path
from . import cabinet_views

app_name = 'cabinet'

urlpatterns = [
    path('', cabinet_views.dashboard, name='dashboard'),
    path('login/', cabinet_views.cabinet_login, name='login'),
    path('logout/', cabinet_views.cabinet_logout, name='logout'),

    # Services
    path('service/', cabinet_views.service_list, name='service_list'),
    path('service/create/', cabinet_views.service_form, name='service_create'),
    path('service/<int:pk>/', cabinet_views.service_form, name='service_edit'),
    path('service/<int:pk>/delete/', cabinet_views.service_delete, name='service_delete'),

    # Products
    path('product/', cabinet_views.product_list, name='product_list'),
    path('product/create/', cabinet_views.product_form, name='product_create'),
    path('product/<int:pk>/', cabinet_views.product_form, name='product_edit'),
    path('product/<int:pk>/delete/', cabinet_views.product_delete, name='product_delete'),
    path('product/<int:pk>/files/', cabinet_views.product_files, name='product_files'),

    # Goods
    path('goods/', cabinet_views.goods_list, name='goods_list'),
    path('goods/create/', cabinet_views.goods_form, name='goods_create'),
    path('goods/<int:pk>/', cabinet_views.goods_form, name='goods_edit'),
    path('goods/<int:pk>/delete/', cabinet_views.goods_delete, name='goods_delete'),
    path('goods/<int:pk>/files/', cabinet_views.goods_files, name='goods_files'),
    path('goods/<int:pk>/upload-file/', cabinet_views.goods_upload_file, name='goods_upload_file'),
    path('goods/<int:pk>/delete-file/<int:file_pk>/', cabinet_views.goods_delete_file, name='goods_delete_file'),

    # Projects
    path('project/', cabinet_views.project_list, name='project_list'),
    path('project/create/', cabinet_views.project_form, name='project_create'),
    path('project/<int:pk>/', cabinet_views.project_form, name='project_edit'),
    path('project/<int:pk>/delete/', cabinet_views.project_delete, name='project_delete'),

    # Blog
    path('blog/', cabinet_views.blog_list, name='blog_list'),
    path('blog/create/', cabinet_views.blog_form, name='blog_create'),
    path('blog/<int:pk>/', cabinet_views.blog_form, name='blog_edit'),
    path('blog/<int:pk>/delete/', cabinet_views.blog_delete, name='blog_delete'),

    # Contacts
    path('contact/', cabinet_views.contact_list, name='contact_list'),
    path('contact/<int:pk>/', cabinet_views.contact_detail, name='contact_detail'),
    path('contact/<int:pk>/delete/', cabinet_views.contact_delete, name='contact_delete'),

    # PageViews
    path('pageviews/', cabinet_views.pageviews_list, name='pageviews_list'),

    # Principles
    path('principle/', cabinet_views.principle_list, name='principle_list'),
    path('principle/create/', cabinet_views.principle_form, name='principle_create'),
    path('principle/<int:pk>/', cabinet_views.principle_form, name='principle_edit'),
    path('principle/<int:pk>/delete/', cabinet_views.principle_delete, name='principle_delete'),

    # Navigation
    path('navlink/', cabinet_views.navlink_list, name='navlink_list'),
    path('navlink/create/', cabinet_views.navlink_form, name='navlink_create'),
    path('navlink/<int:pk>/', cabinet_views.navlink_form, name='navlink_edit'),
    path('navlink/<int:pk>/delete/', cabinet_views.navlink_delete, name='navlink_delete'),

    # Site Settings
    path('sitesetting/', cabinet_views.sitesetting_edit, name='sitesetting_edit'),

    # Hero Section
    path('herosection/', cabinet_views.herosection_edit, name='herosection_edit'),

    # Profile
    path('profile/', cabinet_views.profile, name='profile'),

    # Users (admin management)
    path('users/', cabinet_views.user_list, name='user_list'),
    path('user/create/', cabinet_views.user_create, name='user_create'),
    path('user/<int:pk>/', cabinet_views.user_detail, name='user_detail'),
    path('user/<int:pk>/delete/', cabinet_views.user_delete, name='user_delete'),
    path('user/<int:pk>/toggle-staff/', cabinet_views.user_toggle_staff, name='user_toggle_staff'),
    path('user/<int:pk>/add-goods/', cabinet_views.user_add_goods, name='user_add_goods'),
    path('user/<int:user_pk>/remove-goods/<int:goods_pk>/', cabinet_views.user_remove_goods, name='user_remove_goods'),
    path('user/<int:pk>/add-product/', cabinet_views.user_add_product, name='user_add_product'),
    path('user/<int:user_pk>/remove-product/<int:product_pk>/', cabinet_views.user_remove_product, name='user_remove_product'),

    # Image upload for editor
    path('upload-image/', cabinet_views.upload_image, name='upload_image'),

    # User Settings
    path('usersetting/', cabinet_views.usersetting_list, name='usersetting_list'),
    path('usersetting/create/', cabinet_views.usersetting_form, name='usersetting_create'),
    path('usersetting/<int:pk>/', cabinet_views.usersetting_form, name='usersetting_edit'),
    path('usersetting/<int:pk>/delete/', cabinet_views.usersetting_delete, name='usersetting_delete'),
]
