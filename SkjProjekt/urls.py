"""
URL configuration for SkjProjekt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path
from Obchod import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),

    path('products/', views.products, name='products'),
    path('product_details/<int:product_id>/', views.product_details, name='product_details'),
    path('add_product/', views.add_product, name='add_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),

    path('manage_orders/', views.manage_orders, name='manage_orders'),
    path('orders/', views.orders, name='orders'),
    path('create_order/', views.create_order, name='create_order'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),

    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('increase_cart_quantity/<int:product_id>/', views.increase_cart_quantity, name='increase_cart_quantity'),
    path('decrease_cart_quantity/<int:product_id>/', views.decrease_cart_quantity, name='decrease_cart_quantity'),

    path('manage_employees/', views.manage_employees, name='manage_employees'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('edit_employee/<int:employee_id>/', views.edit_employee, name='edit_employee'),
    path('create_employee/', views.create_employee, name='create_employee'),

    path('manage_categories/', views.manage_categories, name='manage_categories'),
    path('create_category/', views.create_category, name='create_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),

    path('', views.products, name='home'),
]
