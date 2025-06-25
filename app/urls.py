from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('products/', ProductViewList.as_view(), name='product-list'), 
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'), 
    path('products/create/', ProductCreateView.as_view(), name='product-create'), 
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'), 
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'), 
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/add/<int:product_id>/', add_to_card, name='add_to_card'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('order/create/', create_order, name='create_order'),
    path('notifications/', notif_list, name='notifications'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('product/<int:product_id>/review/', leave_review, name='product-review'),
    path('product/<int:product_id>/reviews', product_reviews, name='product-reviews'),
    path('signup', SignUpView.as_view(), name='signup'), 
    path('login', SignInView.as_view(), name='login'), 
    path('logout', SignOutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile-edit'),
    path('profile/add-product/', add_product_view, name='add-product'),
    path('profile/delete-product/<int:product_id>/', delete_product_view, name='delete-product'),
    path('profile/settings/', account_settings_view, name='account-settings')
]