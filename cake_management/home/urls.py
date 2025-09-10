from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),

    # Reviews
    path('reviews/', views.review, name='reviews'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
    path('cake/<int:cake_id>/review/', views.submit_review, name='submit_review'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # Admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit_cake/<int:cake_id>/', views.edit_cake, name='edit_cake'),
    path('delete_cake/<int:cake_id>/', views.delete_cake, name='delete_cake'),
    path('user_details/', views.user_details, name='user_details'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:cake_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease_quantity/<int:cake_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('remove_from_cart/<int:cake_id>/', views.remove_from_cart, name='remove_from_cart'),

    # User
    path('user/', views.user_home, name='user_home'),

    # Order
    path('order-success/', views.order_success, name='order_success'),
    path('purchase/', views.proceed_to_purchase, name='proceed_to_purchase'),

    # Custom Cake Request
    path('custom_cake_request/', views.custom_cake_request_view, name='custom_cake_request'),

    path('create-checkout-session/<int:order_id>/', views.create_checkout_session, name='create_checkout_session'),

    path('profile/edit/', views.edit_profile, name='edit_profile'),
]
