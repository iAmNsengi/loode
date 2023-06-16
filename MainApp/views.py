from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import string
import random
import re
from django.utils.text import slugify
from .models import (
    Client,
    ClientVerify,
    Product,
    Cart,
    Order,
    Category,
    Review,
    PasswordReset,
)
from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings


def generate_random_string(N):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=N))


def handler404(request, exception):
    context = {"title": "Error 404 | lodeShoes"}
    return render(request, "404.html", context)


def handler500(request):
    context = {"title": "Error 500 | lodeShoes"}
    return render(request, "500.html", context)


def handler400(request, exception):
    context = {"title": "Error 400 | lodeShoes"}
    return render(request, "400.html", context)


def handler403(request, exception):
    context = {"title": "Error 403 | lodeShoes"}
    return render(request, "403.html", context)


class Index(View):
    product_list = Category.objects.all()

    def get(self, request):
        client = Client.objects.filter(username=request.user).first()
        cart = Cart.objects.filter(client=client).count()

        context = {
            "products": self.product_list,
            "title": "Home | lodeShoes",
            "cart": cart,
        }
        return render(request, "home.html", context)

    def post(self, request):
        client = Client.objects.filter(username=request.user).first()
        cart = Cart.objects.filter(client=client).count()
        if request.method == "POST":
            sender_name = request.POST.get("name")
            sender_email = request.POST.get("email")
            sender_message = request.POST.get("message")
            try:
                send_mail(
                    subject="A Message from " + sender_name + " at lodeShoes",
                    message=sender_message,
                    from_email=sender_email,
                    recipient_list=[
                        "nsengitech@gmail.com",
                        "lodeshoes22@gmail.com",
                        "ishimweconso@gmail.com",
                    ],
                    fail_silently=False,
                )
            except:
                messages.error(
                    request, "A connection error occurred while sending message retry!."
                )
        context = {
            "products": self.product_list,
            "title": "Home | lodeShoes",
            "cart": cart,
        }
        return render(request, "home.html", context)


def Products(request):
    products = Product.objects.all()
    client = Client.objects.filter(username=request.user).first()
    cart = Cart.objects.filter(client=client).count()
    context = {
        "products": products,
        "title": "shoes | lodeShoes",
        "cart": cart,
    }
    return render(request, "products.html", context)


def ProductDetail(request, id):
    product = Product.objects.get(id=id)
    product_list = Product.objects.all()[:4]
    reviews = Review.objects.filter(product=product)
    client = Client.objects.filter(username=request.user).first()
    cart = Cart.objects.filter(client=client).count()

    if request.method == "POST":
        review = request.POST.get("review")
        print(request.user)

        try:
            user = User.objects.get(username=request.user)
            a_review = Review(product=product, client=user, review=review)
            try:
                a_review.save()
                product.reviews += 1
                product.save()
            except Exception as e:
                messages.error(request, e.error)

        except Exception as e:
            messages.error(request, "You must be logged in to post a review")
            return redirect("/login")
    context = {
        "product": product,
        "products": product_list,
        "title": product.name + " | lodeShoes",
        "cart": cart,
        "reviews": reviews,
    }
    return render(request, "productDetail.html", context)


def addToCart(request, item):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add product to cart!")
        return redirect("products")
    product = Product.objects.get(id=item)
    client = Client.objects.filter(username=request.user).first()
    try:
        Cart.objects.get(item=product, client=client)
        messages.error(
            request,
            "Item already exists in cart try choosing another! Or proceed to checkout",
        )
    except:
        Cart.objects.create(item=product, client=client)
        row = Cart.objects.get(item=product, client=client)
        row.amount = row.get_total_price()
        row.save()
        messages.success(request, "Item added to cart, consider shopping other shoes!")
    return redirect("products")


def removeFromCart(request, item):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add product to cart!")
        return redirect("products")
    item = Product.objects.filter(id=item).first()
    client = Client.objects.get(username=request.user)
    itemExists = Cart.objects.filter(item=item, client=client).first()
    if itemExists is not None:
        cart = itemExists.delete()
        messages.success(request, "Item removed from cart!")
    else:
        messages.error(request, "Item not found in your cart!")
    return redirect("checkout")


def checkout(request):
    products = Product.objects.all()[:3]
    client = Client.objects.filter(username=request.user).first()
    carts = Cart.objects.filter(client=client).all()
    cart = Cart.objects.filter(client=client).count()
    total = Cart.objects.filter(client=client).aggregate(Sum("amount"))

    context = {
        "carts": carts,
        "client": client,
        "products": products,
        "cart": cart,
        "title": "checkout | lodeShoes",
        "total": total,
    }
    return render(request, "checkout.html", context)


def qtyplus(request, id):
    item = Cart.objects.get(id=id)
    item.quantity = item.quantity + 1
    item.amount = item.get_total_price()
    item.save()
    return redirect("http://localhost:8000/checkout#item%s" % id)


def sizeplus(request, id):
    item = Cart.objects.get(id=id)
    item.shoe_size = item.shoe_size + 1
    item.save()
    return redirect("http://localhost:8000/checkout#item%s" % id)


def qtymin(request, id):
    item = Cart.objects.get(id=id)
    if item.quantity > 1:
        item.quantity = item.quantity - 1
        item.amount = item.get_total_price()
        item.save()
    else:
        item.quantity = 1
        item.amount = item.get_total_price()
        item.save()
    return redirect("http://localhost:8000/checkout#item%s" % id)


def sizemin(request, id):
    item = Cart.objects.get(id=id)
    item.shoe_size = item.shoe_size - 1
    item.save()
    return redirect("http://localhost:8000/checkout#item%s" % id)


def confirmOrder(request, client):
    client = Client.objects.filter(username=request.user).first()
    carts = Cart.objects.filter(client=client).all()
    cart = Cart.objects.filter(client=client).count()
    total = Cart.objects.filter(client=client).aggregate(Sum("amount"))

    if request.method == "POST":
        postData = request.POST
        shipping = postData.get("ship")
        address = "_"
        if shipping == "Yes":
            address = postData.get("address")
        i = 1
        if cart >= 1:
            for i in range(cart):
                cartItem = Cart.objects.filter(client=client).first()
                order = Order(
                    product=cartItem.item,
                    client=cartItem.client,
                    quantity_ordered=cartItem.quantity,
                    ship_address=address,
                    shoe_size=cartItem.shoe_size,
                )
                order.amount = order.get_total_price()
                cartItem.delete()
                order.save()
        messages.success(request, "Order Placed successfully!")
        return redirect("/accounts/%s/orders" % request.user)

    context = {
        "carts": carts,
        "client": client,
        "cart": cart,
        "title": "confirm order | lodeShoes",
        "total": total,
    }
    return render(request, "checkoutStep2.html", context)


def about(request):
    client = Client.objects.filter(username=request.user).first()
    cart = Cart.objects.filter(client=client).count()

    context = {
        "title": "About | lodeShoes",
        "cart": cart,
    }
    return render(request, "about.html", context)


class Register(View):
    def get(self, request):
        title = "Register | lodeShoes"
        context = {
            "title": title,
        }
        return render(request, "register.html", context)

    def post(self, request):
        postData = request.POST
        first_name = postData.get("firstname")
        last_name = postData.get("lastname")
        phone = postData.get("phone")
        email = postData.get("email")
        address = postData.get("address")
        username = postData.get("username")
        password1 = postData.get("password1")
        password2 = postData.get("password2")
        values = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "address": address,
            "username": username,
            "phone": phone,
            "password1": password1,
            "password2": password2,
        }
        error_message = None

        if password1 != password2:
            error_message = "Passwords do not match"

        if User.objects.filter(username=username).exists():
            new_username = slugify(username)
            username = new_username + generate_random_string(3)
            error_message = (
                "Username already taken try using :  " + username + "  or try another!"
            )
        client = Client(
            user=None,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            username=username,
            address=address,
        )
        error_message = self.validateClient(client, password1)
        if not error_message:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                user = User.objects.get(username=username)

                client = Client(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    email=email,
                    username=username,
                    address=address,
                )

                client.register()

                code = generate_random_string(6)
                send_mail(
                    subject="Account creation confirmation --- lodeShoes",
                    message=f"Thank you dear {username} for creating an account at lodeshoes! \n Your Email verification code is: \n\n\n  {code}  \n\n\n Thank You! \n LodeShoes Team \n Best Regards",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[
                        email,
                    ],
                    fail_silently=False,
                )
                client = Client.objects.get(username=username)
                try:
                    code_exist = ClientVerify.objects.get(client=client, code=code)
                    code = code_exist.code
                except:
                    pass
                code_obj = ClientVerify(client=client, code=code)
                code_obj.save()
                messages.info(request, "Check your email for Email Verification Code!")
                return redirect("/verify/%s" % username)
            except Exception as e:
                messages.error(request, e)
                return render(request, "register.html", values)
        else:
            title = "Register | lodeShoes"
            values = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": username,
                "phone": phone,
                "password1": password1,
                "password2": password2,
            }
            data = {
                "error": error_message,
                "values": values,
                "title": title,
            }
            messages.error(request, error_message)
            return render(request, "register.html", data)

    def validateClient(self, client, password1):
        error_message = None
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        # compiling regex
        pat = re.compile(reg)
        # searching regex
        mat = re.search(pat, password1)
        if not mat:
            error_message = "Invalid Password, Password should contain uppercase, lowercase, digits and longer than six characters"
        elif client.clientExist():
            error_message = "User with the email already exist!"
        return error_message


def verify(request, username):
    context = {"title": "Account Verification | lodeShoes"}
    client = Client.objects.filter(username=username).first()

    if request.method == "POST":
        code = request.POST.get("code")
        if client.verified is True:
            messages.info(request, "User is already verified!")
            return redirect("/")
        try:
            verify_obj = ClientVerify.objects.get(client=client, code=code)
            client.verified = True
            client.save()
            verify_obj.delete()
            messages.success(request, "Account Verified successfully!")
            return redirect("/login")
        except Exception as e:
            messages.error(request, e)
    return render(request, "emailVerify.html", context)


def resend_verification_code(request, user):
    try:
        client = Client.objects.get(username=user)
        code = ClientVerify.objects.get(client=client)
        send_mail(
            subject="Account creation confirmation --- lodeShoes",
            message=f"Thank you dear {client.username} for creating an account at lodeshoes! \n Your Email verification code is: \n\n\n  {code}  \n\n\n Thank You! \n LodeShoes Team \n Best Regards",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                client.email,
            ],
            fail_silently=False,
        )
        messages.success(
            request, "Account confirmation email sent on your email %s" % client.email
        )
        return redirect("/verify/%s" % client.username)
    except Exception as e:
        return messages.error(request, e)


def forgot_password(request):
    context = {"title": "Forgot Password | lodeShoes"}
    if request.method == "POST":
        email = request.POST.get("email")
        key = generate_random_string(12)

        try:
            user = User.objects.get(email=email)
            client = Client.objects.get(user=user)
            reset_object = PasswordReset(email=client, key=key)
            try:
                reset_object.save()
                send_mail(
                    subject="Password Reset",
                    message=f"Dear {user.username} \n You have requested a password reset at Lodeshoes\nFollow this link to proceed\n\nhttp://localhost:8000/resetpassword/{key}/\n\nThank You! \n LodeShoes Team \n Best Regards",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[
                        email,
                    ],
                    fail_silently=False,
                )
                messages.success(
                    request, "Password reset details were sent to your email inbox!"
                )
            except Exception as e:
                messages.error(request, e)
        except Exception as e:
            messages.error(request, e)
            return redirect("/forgotpassword")
    return render(request, "forgot_password.html", context)


def ResetPassword(request, key):
    try:
        reset_object = PasswordReset.objects.get(key=key)
        if request.method == "POST":
            user = User.objects.get(username=reset_object.email.user)
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if password1 != password2:
                messages.error(request, "Passwords doesnot match!")
                return redirect(f"/resetpassword/{key}/")
            else:
                user.set_password(password1)
                user.save()
                messages.success(
                    request, "Password reset Successfully now you can login!"
                )
                reset_object.delete()
                return redirect("/login/")
    except Exception as e:
        messages.error(request, e)
        return redirect("/forgotpassword")
    return render(request, "reset_password.html")


class Login(View):
    def get(self, request):
        if self.request.user.is_authenticated:
            return redirect("homepage")

        title = "Login | lodeShoes"
        context = {"title": title}
        return render(request, "login.html", context)

    def post(self, request):
        postData = self.request.POST
        username = postData.get("email_or_user")
        password = postData.get("password")
        error_message = None
        title = "Login | lodeShoes"
        values = {
            "username": username,
            "password": password,
            "title": title,
        }
        if not User.objects.filter(username=username).exists():
            error_message = "User not found!"
        else:
            user = authenticate(request, username=username, password=password)

        if User.objects.filter(email=username).exists():
            error_message = None
            try:
                theuser = User.objects.get(email=username)
                username = theuser.username
            except:
                error_message = "An Internal Server Error Occurred Try again Later!"
        try:
            is_verified = Client.objects.get(username=username)
            if is_verified.verified is False:
                messages.error(
                    request,
                    "Account not Verified check your email for verification code!",
                )
                return redirect("/verify/username")
        except:
            pass

        user = authenticate(request, username=username, password=password)
        if user is None:
            error_message = "User with given credentials not found!"

        if error_message is None:
            login(request, user)
            return redirect("homepage")
        messages.error(request, error_message)
        return render(request, "login.html", values)


def Logout(request):
    logout(request)
    return redirect("login")


def PersonalSettings(request, user):
    title = str(request.user) + " | Settings"
    client = Client.objects.get(username=user)
    cart = Cart.objects.filter(client=client).count()

    if client is None:
        messages.error(request, "Client account not found!")
        return redirect("home")
    else:
        if request.method == "POST":
            postData = request.POST
            client.first_name = postData.get("firstname")
            client.last_name = postData.get("lastname")
            client.phone = postData.get("phone")
            client.email = postData.get("email")
            client.save()
            messages.success(request, "Client changes saved successfully!")

    context = {
        "title": title,
        "client": client,
        "cart": cart,
    }
    return render(request, "settings.html", context)


def MyOrders(request, user):
    title = str(request.user) + " | My Orders"
    client = Client.objects.filter(username=request.user).first()
    orders = Order.objects.filter(client=client).order_by("-order_date").all()
    cart = Cart.objects.filter(client=client).count()
    total = Order.objects.filter(client=client).aggregate(Sum("amount"))

    context = {
        "title": title,
        "orders": orders,
        "total": total,
        "cart": cart,
        "client": client,
    }
    return render(request, "orders.html", context)


def UploadProof(request, user, id):
    order = Order.objects.get(id=id)

    if request.method == "POST":
        img = request.FILES.get("image")
        order.proof = img
        order.comment = (
            "Payment under review! We will get back to you on your phone number!"
        )
        order.order_status = 1
        client = Client.objects.filter(username=request.user).first()
        client_email = client.email
        client_phone = client.phone
        receiver_name = client.first_name + " " + client.last_name
        receiver_email = client.email
        order_amount = order.amount
        try:
            send_mail(
                subject="Order Received lodeShoes",
                message=f"Thank you dear {receiver_name} for placing an order to lodeshoes! \n Now you should pay an amount of {order_amount} either to our Mobile Money account +250785816971 or at Bank Of Kigali on account 123-1234-12345. \n After you should get back to the system and upload a screenshot of your payment! \n Thank You! \n LodeShoes Team \n Best Regards",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[
                    receiver_email,
                ],
                fail_silently=False,
            )
            send_mail(
                subject="An order from lodeShoes",
                message=f"Hello Admin,\nUser {receiver_name} with email {client_email} and phone number {client_phone}\nHas placed an order to lodeshoes suming an amount of {order_amount}, with a proof of payment! \nCheck to the system the uploaded a screenshot of  payment! \nThank You! \nLodeShoes Robot \nBest Regards",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=["nsengitech@gmail.com", "ishimweconso@gmail.com"],
                fail_silently=False,
            )
            order.product.qty -= 1
            order.save()
            messages.success(
                request,
                "Screenshot uploaded successfully! Check your email for further instructions!",
            )
        except:
            messages.error(
                request,
                f"Try uploading the screenshot again! \nAn unexpected error occurred!",
            )
        return redirect("/accounts/%s/orders" % request.user)
