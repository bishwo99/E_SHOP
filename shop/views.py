from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from .forms import RegistrationForm,RatingForm,CheckoutForm
from . import models
from django.db.models import Max, Min, Avg, Q
from . import forms


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
        'max_price' : max_price,
    })   

def product_list(request,slug):
    product = get_object_or_404(models.Product, slug = slug, available = True)
    related_products = models.Product.objects.filter(category = product.category).exclude(id = product.id)

    user_rating = None
    if request.user.is_authenticate:
        try:
            user_rating = models.Rating.objects.get(product=product, user = request.user)
        except models.Rating.DoesNotExist:
            pass       
    rating_form = RatingForm(instance = user_rating)

    return render(request,'',{
        'product' : product,
        'related_products' : related_products,
        'rating_form' : rating_form,
        'user_rating' : user_rating,
    })

    # Rate Product
    # Loged in user can rate the product, Is the user purchased the product or not

def rate_product(request, product_id):
    product = get_object_or_404(models.Product, id = product_id)
    ordered_items = models.OrderItem.objects.filter(
        order__user = request.user,
        product = product,
        order__paid = True
        )
    if not ordered_items.exists():
        messages.error(request, 'You can only rate products you have purchased.')
        return redirect('')
    try:
        rating = models.Rating.objects.get(product = product, user = request.user)
    except models.Rating.DoesNotExist:
        rating = None

        # Jodi rating age diye thake tahole form e age theke rating show korbe, sekhetre instance = user rating thakbe

        #  jodi rating na diye thake tahole instance = None thakbe, tahole form e kono rating show korbe na



    if request.method == 'POST':
        form = RatingForm(request.POST, instance = rating)
        if form.is_valid():
            rating = form.save(commit = False)
            rating.product = product
            rating.user = request.user
            rating.save()
            return redirect('')
        else:
            form = RatingForm(instance = rating)
    return render(request,'',{
        'form' : form,
        'product' : product,
            
    })

# Everything about Cart - Features
# cart_detail - Temporar order
# Cart item add - ok
# cart item remove - ok
# cart item update - ok
# checkout


def cart_add(request, product_id):
    product = get_object_or_404(models.Product, id = product_id)
    # User er card ache kina
    # Jodi cart na thake tahole sheta identify kora

    try: 
        cart = models.Cart.objects.get(user = request.user)

    # Jodi na thake tahole cart ekta banabo.
    except models.Cart.DoesNotExist:
        cart = models.Cart.objects.create(user = request.user)
    # Cart e item add korbo

    # Case 1: Cart e item ache

    try:
        cart_item = models.CartItem.objects.get(cart = cart, product = product)
        cart_item.quantity += 1
        cart_item.save()
    # Case 2: Cart e item nai
    except models.CartItem.DoesNotExist:
        cart_item = models.CartItem.objects.create(cart = cart, product = product, quantity = 1)
    messages.success(request, f"{product.name} has been added to your cart")
    return redirect(request,'')

# Cart Update
# Cart item quantity increase/decrease korte parbo

def cart_update(request,product_id):
    # Cart Konta
    # Cart Item konta
    # Product gulo Cart Item e or Stock e available ache kina
    cart = get_object_or_404(models.Cart, user = request.user)
    product = get_object_or_404(models.Product, product_id)
    cart_item = get_object_or_404(models.CartItem, cart = cart, product = product)

    quantity = int(request.POST.get('quantity',1))

    # There are important case

    # Cart item stock e ache 20 ta but user order korte chacche 40 ta

    # Cart item update korte korte jokhon quantity 0 te chole ashbe tokhon actually user oi item ta delete korte chacche

    if quantity <= 0:
        cart_item.delete()
        messages.success(request, f"{product.name} has been deleted successfully from your cart!")

    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, "Cart update succsessfully!")
    return redirect()


def cart_remove(request,product_id):

    cart = get_object_or_404(models.Cart, user = request.user)
    product = get_object_or_404(models.Product, product_id)
    cart_item = get_object_or_404(models.CartItem, cart = cart, product = product)

    cart_item.delete()
    messages.success(request, f"{product.name} has been deleted from your cart!!")
    return redirect("")

def cart_details(request, product_id):
    # Case01: User er cart nai
    # Case02: User er cart ache

    try:
        cart = models.Cart.objects.get(user = request.user)
    except models.Cart.DoesNotExist:
        cart = models.Cart.objects.create(user = request.user)

    return render(request,'', {'cart': cart})


# For checkout
# Cart er datagulo niye ashbo
# Cart empty thakle message dibo
def checkout(request):
    cart = models.Cart.objects.get(user = request.user)
    try:
        if not cart.items.exists():
            messages.warning(request,'Your cart is empty.')
    except models.Cart.DoesNotExist():
        messages.warning(request,'Your cart is empty.')
        return redirect(request,'')

    #Checkout Form ta fillup korbe
    if request.method == 'POST':
        form = forms.CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False) # object create korbe but database e jabena
            order.user = request.user
            order.save() # order kora hoye geche

        for item in cart.item.all():
            models.OrderItem.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                price = item.product.price,
            )
            #order kora done

        cart.item.all().delete() # After completing order those item, cart will be removed
        request.session['order_item'] = order.id
        return redirect('')
    else:
        form = forms.CheckoutForm()
    return render(request,'',{
        'cart' : cart,
        'form' : form,
    })

# Payment feature

#Payment Success
#Payment Fail
#Payment Cancel

def payment_success(request, order_id):
    order= get_object_or_404(models.Order, user = request.user, id = order_id)
    order.paid = True
    order.status = 'Processing'
    order.transaction_id = order_id
    order.save()

    order_items = order.order_items.all()
    for item in order_items:
        product = item.prodcut
        product.stock -= item.quantity

        #It means, product ache 20 ta and jodi product 40 ta order kora hoye thake tokhon stock quantity negative hoyte parena ejonne 0 kore dibo
        if product.stock <0:
            product.stock = 0
        product.save()

    # Confirmation message
    messages.success(request, 'Payment Successful!')
    return render(request,'', {'order' : order})


def payment_fail(request,order_id):
    order = get_object_or_404(models.Order, id = order_id, user = request.user)
    order.status = 'canceled'
    order.save()

    messages.warning(request, 'Your Payment is cancelled!')
    return redirect('')








        

