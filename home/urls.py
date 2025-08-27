from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cakelist/', views.cakelist, name='cakelist'),
    path('cart/', views.cart, name='cart'),
    path('review/', views.review, name='review'),

    # User Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Admin
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_cake/', views.add_cake, name='add_cake'),  # <-- ADD THIS LINE
    path('edit_cake/<int:cake_id>/', views.edit_cake, name='edit_cake'),
    path('delete_cake/<int:cake_id>/', views.delete_cake, name='delete_cake'),
    path('user_details/', views.user_details, name='user_details'),

    # Cart & Reviews
    path('add_to_cart/<int:cake_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cake_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
]