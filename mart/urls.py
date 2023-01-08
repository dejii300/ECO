from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('user/', views.store, name='store'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order/', views.processOrder, name='process_order'),

    
    path("", views.home, name="home"),
    path("register/", views.registerPage, name="register"),
    path("orders/", views.userPage, name="user_page"),
    path("setting/", views.settingPage, name="setting-page"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("product/", views.products, name="product"),
    path("customer/<str:pk_test>", views.customer, name="customer"),
    path("create_order/<str:pk>", views.createOrder, name="create_order"),
    path("update_order/<str:pk>", views.updateOrder, name="update_order"),
    path("delete_order/<str:pk>", views.deleteOrder, name="delete_order"),

    
    

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), name='reset_password'),

    path('reset_password_send/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_sent.html'),
     name='password_reset_done'),

    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_form.html'),
     name='password_reset_confirm'),

    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_done.html'),
     name='password_reset_complete'),
]