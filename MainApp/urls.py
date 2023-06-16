from django.urls import path
from .views import *

urlpatterns = [
    path("", Index.as_view(), name="homepage"),
    path("login/", Login.as_view(), name="login"),
    path("forgotpassword/", forgot_password, name="forgot_password"),
    path("resetpassword/<str:key>/", ResetPassword, name="reset-password"),
    path("logout/", Logout, name="logout"),
    path("register/", Register.as_view(), name="register"),
    path("about/", about, name="about"),
    path("verify/<str:username>", verify, name="verify"),
    path("resend/<str:user>", resend_verification_code, name="resend"),
    path("products", Products, name="products"),
    path("products/<str:id>", ProductDetail, name="productDetail"),
    path("add-to-cart/<str:item>", addToCart, name="add-to-cart"),
    path("remove-from-cart/<str:item>", removeFromCart, name="remove-from-cart"),
    path("accounts/<str:user>", PersonalSettings, name="accounts"),
    path("accounts/<str:user>/orders", MyOrders, name="orders"),
    path("accounts/<str:user>/orders/<str:id>", UploadProof, name="proof"),
    path("checkout", checkout, name="checkout"),
    path("confirm/<str:client>", confirmOrder, name="confirm"),
    path("qtyplus/<str:id>", qtyplus),
    path("qtymin/<str:id>", qtymin),
    path("sizemin/<str:id>", sizemin),
    path("sizeplus/<str:id>", sizeplus),
]
