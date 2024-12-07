
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
   path('create-order/', views.CreateOrderView.as_view(), name='create-order'),
    path('verify-payment/', views.VerifyPaymentView.as_view(), name='verify-payment'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order_history/', views.order_history, name='order_history'),
    path('invoice/<str:order_id>/', views.generate_invoice, name='generate_invoice'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
