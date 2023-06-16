from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import sys
from PIL import Image
import PIL


# Create your models here.
class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    username = models.CharField(max_length=30)
    address = models.CharField(max_length=200)
    verified = models.BooleanField(default=False)

    # to save the datas
    def register(self):
        self.save()

    @staticmethod
    def get_client_by_username(username):
        try:
            return Client.objects.get(username=username)
        except:
            return False

    @staticmethod
    def get_client_by_email(email):
        try:
            return Client.objects.get(email=email)
        except:
            return False

    def clientExist(self):
        if Client.objects.filter(email=self.email):
            return True
        return False

    def __str__(self):
        return self.username


class ClientVerify(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)


class Category(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField()
    image = models.ImageField(upload_to="category/")

    # def save(self, *args, **kwargs):
    #     base_width = 360
    #     image = Image.open(self.image)
    #     width_percent = base_width / float(image.size[0])
    #     hsize = int((float(image.size[1]) * float(width_percent)))
    #     image = image.resize((base_width, hsize), PIL.Image.ANTIALIAS)
    #     image.save(f"media/category/{self.image}.jpg")
    #     with open(f"{self.image}.jpg", "rb") as fd:
    #         img = fd.read()
    #     self.image.save(f"media/category/{self.image}.jpg", ContentFile(img), save=True)
    #     super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    qty = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    image = models.ImageField(upload_to="products")
    image2 = models.ImageField(upload_to="products", blank=True, null=True)
    image3 = models.ImageField(upload_to="products", blank=True, null=True)
    image4 = models.ImageField(upload_to="products", blank=True, null=True)
    reviews = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    review = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.client.username


STATUS = ((0, "Order Received"), (1, "Payment Received"), (2, "Delivered"))


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    quantity_ordered = models.IntegerField(default=1)
    shoe_size = models.IntegerField(default=42)
    amount = models.IntegerField(default=0)
    ship_address = models.CharField(max_length=100, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    proof = models.ImageField(upload_to="proofs/")
    order_status = models.IntegerField(choices=STATUS, default=0)
    comment = models.TextField(
        default="Upload your screenshot of your payment!", null=True, blank=True
    )

    def __str__(self):
        return self.client.username

    def get_total_price(self):
        return self.product.price * self.quantity_ordered


class Cart(models.Model):
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    shoe_size = models.IntegerField(default=42)
    amount = models.IntegerField(default=0, null=True)

    def get_total_price(self):
        return self.item.price * self.quantity

    def __str__(self):
        return self.item.name


class PasswordReset(models.Model):
    email = models.ForeignKey(Client, on_delete=models.CASCADE)
    key = models.CharField(max_length=20)
