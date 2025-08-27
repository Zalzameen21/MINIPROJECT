from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from .models import Cake, CakeReview, Order, Cart
from .forms import ReviewForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

# -------------------- Public Views --------------------
def index(request):
    cakes = Cake.objects.all()
    return render(request, "index.html", {'cakes': cakes})

def cakelist(request):
    cakes = Cake.objects.all()
    return render(request, "cakelist.html", {'cakes': cakes})

def review(request):
    reviews = CakeReview.objects.all().select_related("user", "cake")
    return render(request, 'review.html', {'reviews': reviews})

# -------------------- Cart Views --------------------
@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.cake.price * item.quantity for item in cart_items)
    return render(request, "cart.html", {"cart_items": cart_items, "total_price": total_price})

@login_required(login_url='login')
def add_to_cart(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, cake=cake)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required(login_url='login')
def remove_from_cart(request, cake_id):
    cart_item = get_object_or_404(Cart, user=request.user, cake_id=cake_id)
    cart_item.delete()
    return redirect('cart')

# -------------------- Cake Detail & Review --------------------
def cake_detail(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    reviews = CakeReview.objects.filter(cake=cake).select_related("user")
    form = None

    if request.user.is_authenticated:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.cake = cake
                review.user = request.user
                review.save()
                return redirect("cake_detail", cake_id=cake.id)
        else:
            form = ReviewForm()

    return render(request, "cake_detail.html", {
        "cake": cake,
        "reviews": reviews,
        "form": form,
    })

# -------------------- Customer Signup/Login/Logout --------------------
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        role = request.POST.get('role')  # get role from dropdown
        if form.is_valid():
            user = form.get_user()
            if role == 'admin' and not user.is_staff:
                # only staff can login as admin
                return render(request, 'login.html', {'form': form, 'error': 'Not an admin account'})
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'form': form, 'error': 'Invalid credentials'})
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

# -------------------- Admin/User Register (Admin Page) --------------------
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # optional
        full_name = request.POST.get('name')
        address = request.POST.get('address')  # optional

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('admin_login')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=full_name
        )
        user.save()
        messages.success(request, 'Account created successfully. You can now login.')
        return redirect('admin_login')
    return redirect('admin_login')

# -------------------- Admin Check/Login/Dashboard --------------------
def is_admin(user):
    return user.is_authenticated and user.is_staff

def admin_login(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            error = 'Invalid credentials or not an admin account'
    return render(request, 'admin.html', {'error': error})

@login_required(login_url='/admin_login/')
@user_passes_test(is_admin, login_url='index')
@csrf_protect
def admin_dashboard(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        size = request.POST.get('size')
        shape = request.POST.get('shape')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        if name and price and size and shape and image:
            Cake.objects.create(
                name=name,
                price=price,
                size=size,
                shape=shape,
                description=description,
                image=image
            )
            messages.success(request, "Cake added successfully!")
        else:
            messages.error(request, "All fields are required!")
        return redirect('admin_dashboard')

    cakes = Cake.objects.all()
    return render(request, 'admin_dashboard.html', {'cakes': cakes})

@login_required(login_url='/admin_login/')
@user_passes_test(is_admin, login_url='index')
def edit_cake(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    if request.method == 'POST':
        cake.name = request.POST.get('name')
        cake.price = request.POST.get('price')
        cake.size = request.POST.get('size')
        cake.shape = request.POST.get('shape')
        cake.description = request.POST.get('description')
        if request.FILES.get('image'):
            cake.image = request.FILES.get('image')
        cake.save()
        messages.success(request, "Cake updated successfully!")
        return redirect('admin_dashboard')
    return render(request, 'add_edit_cake.html', {'cake': cake})

@login_required(login_url='/admin_login/')
@user_passes_test(is_admin, login_url='index')
def delete_cake(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    cake.delete()
    messages.success(request, "Cake deleted successfully!")
    return redirect('admin_dashboard')

@login_required(login_url='/admin_login/')
@user_passes_test(is_admin, login_url='index')
def user_details(request):
    users = User.objects.all()
    orders = Order.objects.select_related('user', 'cake').all()
    return render(request, 'user_details.html', {'users': users, 'orders': orders})
