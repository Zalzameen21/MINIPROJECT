from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse

from .models import Cake, CakeReview, Order, Cart, CustomCakeRequest, Register, OrderItem
from .forms import CakeReviewForm
from .forms import CakeForm
from .forms import EditProfileForm
import stripe
from .models import Order


# -------------------- Public Views --------------------
def index(request):
    cakes = Cake.objects.all()
    return render(request, "index.html", {'cakes': cakes})

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
def decrease_quantity(request, cake_id):
    cart_item = get_object_or_404(Cart, user=request.user, cake_id=cake_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

@login_required(login_url='login')
def remove_from_cart(request, cake_id):
    cart_item = get_object_or_404(Cart, user=request.user, cake_id=cake_id)
    cart_item.delete()
    return redirect('cart')


# -------------------- Cake Detail & Review --------------------
@login_required(login_url='login')
def cake_detail(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    reviews = CakeReview.objects.filter(cake=cake).select_related("user")

    if request.method == "POST":
        form = CakeReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.cake = cake
            review.user = request.user
            review.save()
            return redirect('cake_detail', cake_id=cake.id)
    else:
        form = CakeReviewForm()

    return render(request, "cake_detail.html", {
    "cake": cake,
    "reviews": reviews,
    "form": form,
})



# -------------------- Login/Logout --------------------
def login_view(request):
    error = None
    if request.method == "POST":
        role = request.POST.get('role')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if role == 'admin' and user.is_superuser:
                return redirect('admin_dashboard')
            elif role == 'user' and not user.is_superuser:
                return redirect('user_home')
            else:
                logout(request)
                error = "Role mismatch. Please select the correct role."
        else:
            error = "Invalid username or password"

    return render(request, 'admin.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('login')


# -------------------- Register --------------------
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        full_name = request.POST.get('name', '').strip() or username
        address = request.POST.get('address', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email or '',
            first_name=full_name
        )

        Register.objects.create(
            user=user,
            full_name=full_name,
            dob="2000-01-01",
            phone=phone or "0000000000",
            address=address or "Not provided"
        )

        messages.success(request, 'Account created successfully. You can now login.')
        return redirect('login')

    return render(request, 'register.html')


# -------------------- Add Cake --------------------
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='index')
def add_cake(request):
    if request.method == 'POST':
        form = CakeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Cake added successfully!")
            return redirect('admin_dashboard')
    else:
        form = CakeForm()
    return render(request, 'add_edit_cake.html', {'form': form})


# -------------------- Edit Cake --------------------
@login_required(login_url='login')
@user_passes_test(lambda u: u.is_superuser, login_url='index')
def edit_cake(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    if request.method == 'POST':
        form = CakeForm(request.POST, request.FILES, instance=cake)
        if form.is_valid():
            form.save()
            messages.success(request, "Cake updated successfully!")
            return redirect('admin_dashboard')
    else:
        form = CakeForm(instance=cake)
    return render(request, 'add_edit_cake.html', {'form': form, 'cake': cake})


# -------------------- Admin Dashboard --------------------
def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='index')
@csrf_protect
def admin_dashboard(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_order':
            order_id = request.POST.get('order_id')
            new_status = request.POST.get('status')
            try:
                order = Order.objects.get(id=order_id)
                order.status = new_status
                order.save()
                messages.success(request, f"Order #{order_id} status updated to {new_status}!")
            except Order.DoesNotExist:
                messages.error(request, "Order not found!")
            return redirect('admin_dashboard')

        elif action in ['Accepted', 'Rejected']:
            request_id = request.POST.get('request_id')
            try:
                custom_request = CustomCakeRequest.objects.get(id=request_id)
                custom_request.status = action
                custom_request.save()
                messages.success(request, f"Request {action.lower()} successfully!")
            except CustomCakeRequest.DoesNotExist:
                messages.error(request, "Custom request not found!")
            return redirect('admin_dashboard')

        else:
            # Handle Add Cake form submission here
            name = request.POST.get('name')
            price = request.POST.get('price')
            size = request.POST.get('size')
            shape = request.POST.get('shape')
            description = request.POST.get('description')
            image = request.FILES.get('image')

            if name and price and size and shape and image:
                cake = Cake.objects.create(
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
            
            return redirect('admin_dashboard')  # Prevent resubmission

    # Handle GET requests or POST after processing
    cakes = Cake.objects.all()
    users = User.objects.all().select_related('register_info')
    orders = Order.objects.select_related('user').order_by('-ordered_at')
    reviews = CakeReview.objects.select_related('user', 'cake').all()
    custom_requests = CustomCakeRequest.objects.select_related('user', 'reference_cake').all()

    return render(request, 'admin_dashboard.html', {
        'cakes': cakes,
        'users': users,
        'orders': orders,
        'reviews': reviews,
        'custom_requests': custom_requests,
        'order_status_choices': [choice[0] for choice in Order.STATUS_CHOICES]
    })


@login_required(login_url='login')
@user_passes_test(is_admin, login_url='index')
def delete_cake(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    cake.delete()
    messages.success(request, "Cake deleted successfully!")
    return redirect('admin_dashboard')

@login_required(login_url='login')
@user_passes_test(is_admin, login_url='index')
def user_details(request):
    users = User.objects.all()
    orders = Order.objects.prefetch_related('items').all()
    return render(request, 'user_details.html', {'users': users, 'orders': orders})


# -------------------- User Home --------------------
@login_required(login_url='login')
def user_home(request):
    cakes = Cake.objects.all()
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'user.html', {'cakes': cakes, 'orders': orders})


# -------------------- Order --------------------
@login_required(login_url='login')
def proceed_to_purchase(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')  # Or show an error message

    # Calculate total price
    total_price = sum(item.cake.price * item.quantity for item in cart_items)

    # Create a new Order
    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        status='Pending'
    )

    # Create OrderItem entries
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            cake=item.cake,
            quantity=item.quantity,
            price=item.cake.price
        )

    # Clear the cart after ordering
    cart_items.delete()

    return render(request, 'order_success.html', {'order': order})

@login_required(login_url='login')
def order_success(request):
    return render(request, 'order_success.html')


# -------------------- Custom Cake Requests --------------------
@login_required(login_url='login')
def custom_cake_request_view(request):
    cake_id = request.GET.get('cake_id')
    reference_cake = None
    if cake_id:
        reference_cake = get_object_or_404(Cake, id=cake_id)

    if request.method == "POST":
        CustomCakeRequest.objects.create(
            user=request.user,
            reference_cake=reference_cake,
            cake_name=None if reference_cake else request.POST.get('cake_name'),
            flavor=request.POST.get('flavor'),
            shape=request.POST.get('shape'),
            size=request.POST.get('size'),
            layers=int(request.POST.get('layers')),
            weight=float(request.POST.get('weight')),
            quantity=int(request.POST.get('quantity')),
            toppings=request.POST.get('toppings'),
            message=request.POST.get('message'),
            details=request.POST.get('details'),
            status='Pending'
        )
        messages.success(request, "Custom cake request submitted successfully!")
        return redirect('user_home')

    # Fetch user's previous requests to show status
    user_requests = CustomCakeRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'custom_cake_request.html', {
        'reference_cake': reference_cake,
        'user_requests': user_requests
    })


# -------------------- Submit Review --------------------
@login_required(login_url='login')
def submit_review(request, cake_id):
    cake = get_object_or_404(Cake, pk=cake_id)
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            CakeReview.objects.create(
                cake=cake,
                user=request.user,
                rating=rating,
                comment=comment
            )
            return redirect('submit_review', cake_id=cake.id)  # refresh page
    
    reviews = CakeReview.objects.filter(cake=cake).order_by("-created_at")
    return render(request, "review.html", {"cake": cake, "reviews": reviews})

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'order_success.html', context)




stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    YOUR_DOMAIN = 'http://127.0.0.1:8000'  # or your domain in production

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': int(order.total_price * 100),  # Stripe expects amount in paise
                'product_data': {
                    'name': f"Order #{order.id}",
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=YOUR_DOMAIN + '/payment-success/',
        cancel_url=YOUR_DOMAIN + '/payment-cancelled/',
    )
    return JsonResponse({'id': checkout_session.id})

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')

@login_required
def edit_profile(request):
    try:
        register_info = request.user.register_info
    except Register.DoesNotExist:
        # Handle the case if register_info is missing
        register_info = Register.objects.create(user=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=register_info)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('user_home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EditProfileForm(instance=register_info)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': request.user
    })

