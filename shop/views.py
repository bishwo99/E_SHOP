from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .forms import RegistrationForm,RatingForm,CheckoutForm
from . import models
from django.db.models import Max, Min, Avg, Q


# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request,user)
            redirect('')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, '')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request, "Registration Successfull")
            redirect()
    else:
        form = RegistrationForm()
    return render(request,'', {'form' : form})

def logout_view(request):
    logout(request)
    redirect('')

# Creating Homepage

def home(request):
    featured_product = models.Product.objects.filter(available = True).order_by('-created_at') [:8] # Descending Order
    categories = models.Category.objects.all()
    return render(request, '', {'featured_product': featured_product, 'categories': categories})

def product_list(request, category_slug = None):  # Slug means, converting element info within link 
    category = None
    categories = models.Category.objects.all()
    products = models.Product.objects.all()

    if category_slug:
        category = get_object_or_404(models.Category, category_slug)
        products = products.filter(category = category)

    min_price = products.aggregate(Min('price'))['price__min']  
    max_price = products.aggregate(Max('price'))['price__max']

    if request.GET.get('min_price'):
        products = products.filter(price__gte = request.GET.get('min_price'))  # Use filtering function
    if request.GET.get('max_price'):
        products = products.filter(price__lte = request.GET.get('max_price'))

    if request.GET.get('rating'):
        products = products.annotate(avg_rating = Avg('ratings__rating')).filter(avg_rating = request.GET.get('rating')) #annotate means creating another variable corresponding another object with present variable

    if request.GET.get('search'):   
        query = request.GET.get('search')   #Search queries
        products = products.filter(
            Q(name__icontains = query)|
            Q(description__icontains = query)|
            Q(category__name__icontains = query)  
        )

    return(request,'',{
        'category' : category,
        'categories' : categories,
        'products' : products,
        'min_price' : min_price,
        'max_price' : max_price

    })   