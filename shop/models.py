from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique = True)
    description = models.TextField(blank=True)

    class Meta():
        verbose_name_plural = 'Categories'
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique= True)
    category = models.ForeignKey(Category,on_delete= models.CASCADE, related_name= 'products')
    description = models.TextField()
    price = models.DecimalField(max_digits=100, decimal_places=2)
    stock = models.PositiveBigIntegerField(default=1)
    available = models.BooleanField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d') #products/date

    def __str__(self):
        return self.name

    def avg_rating(self):
        ratings = self.ratings.all()
        if ratings.count>0:
            return sum([rating.rating for rating in ratings])/ratings.count()

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"

class Cart(models.Model):
    user = models.OneToOneField(User,on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    #total price
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all()) #Confusion ache ekhane

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} X {self.product.name}"
    
    #Item price 
    def get_cost(self):
        return self.quantity * self.product.price

class Order(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled' , 'Canceled'),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=12)
    postal_code = models.CharField()
    city = models.CharField(max_length=100)
    note = models.TextField()
    paid = models.BooleanField(default= False)
    transaction_id = models.CharField(max_length=100)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Order #{self.id}"
    def get_total_cost(self):
            return sum(item.get_cost() for item in self.order_items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete= models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_cost(self):
        return self.quantity * self.product.price
