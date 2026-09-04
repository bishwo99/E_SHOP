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
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    