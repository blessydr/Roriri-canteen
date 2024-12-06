from django.shortcuts import render, redirect
from .models import MenuItem, Cart, CartItem, Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Retrieve payment details
        payment_id = request.POST['razorpay_payment_id']
        order_id = request.POST['razorpay_order_id']
        signature = request.POST['razorpay_signature']

        # Verify the payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            # Verify the payment
            razorpay_client.utility.verify_payment_signature(params_dict)
            # Mark the payment as successful in your database
            return JsonResponse({'status': 'Payment Successful'})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'Payment Failed'})

    return JsonResponse({'status': 'Invalid request'})

# RAZORPAY_KEY_ID = 'rzp_test_1DP2O7wfj6zZAW'
# RAZORPAY_KEY_SECRET = '41O5HG71Yt8gctMtxo2Q6l9A'
def create_order(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')  # Get the order amount from the frontend
        
        # Create a Razorpay Order
        order = razorpay_client.order.create({
            'amount': int(amount) * 100,  # Amount should be in paise (i.e., 100 paise = 1 INR)
            'currency': 'INR',
            'payment_capture': '1',
        })

        # Save order details in your database
        order_id = order['id']
        Order.objects.create(
            user=request.user,
            amount=amount,
            order_id=order_id
        )
        
        return JsonResponse({
            'order_id': order_id,
            'amount': amount
        })
    
    return render(request, 'order/payment_page.html')

def payment_callback(request):
    if request.method == 'POST':
        # Get the payment details
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        # Verify the payment
        try:
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # Payment is successful, update order status
            order = Order.objects.get(order_id=order_id)
            order.payment_status = 'Completed'
            order.save()

            return redirect('payment_success')

        except razorpay.errors.SignatureVerificationError:
            return redirect('payment_failure')

def payment_success(request):
    return render(request, 'order/payment_success.html')

def payment_failure(request):
    return render(request, 'order/payment_failure.html')

def menu_list(request):
    # Start with all items
    items = MenuItem.objects.all()

    # Get query parameters
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    category = request.GET.get('category', '')
    is_vegetarian = request.GET.get('is_vegetarian', '')

    # Filter by name (if search query is provided)
    if search_query:
        items = items.filter(name__icontains=search_query)
    
    # Filter by price range (if min or max price is provided)
    if min_price:
        try:
            items = items.filter(price__gte=float(min_price))
        except ValueError:
            pass  # If value is not a valid float, ignore
    if max_price:
        try:
            items = items.filter(price__lte=float(max_price))
        except ValueError:
            pass  # If value is not a valid float, ignore

    # Filter by category
    if category:
        items = items.filter(category=category)

    # Filter by vegetarian option
    if is_vegetarian:
        items = items.filter(is_vegetarian=is_vegetarian == 'True')

    return render(request, 'menu.html', {'items': items})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Log the user in
            messages.success(request, 'Login successful!')
            return redirect('menu_list')  # Redirect to home page or menu list
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('user_login')  # Redirect to login page if authentication fails

    return render(request, 'login.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)  # Log the user out
    return redirect('user_login')  # Redirect to login page after logging out

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        # Check if passwords match
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return redirect('register')
        
        # Create a new user if everything is valid
        user = User.objects.create_user(username=username, password=password)
        user.save()
        
        # Log the user in automatically after registration
        login(request, user)
        
        messages.success(request, 'Account created successfully!')
        return redirect('menu_list')  # Redirect to the home page or dashboard after successful registration

    return render(request, 'register.html')

# def menu_list(request):
#     menu_items = MenuItem.objects.all()
#     return render(request, 'menu_list.html', {'menu_items': menu_items})

@login_required
def add_to_cart(request, item_id):
    item = MenuItem.objects.get(id=item_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=item)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'cart_detail.html', {'items': items, 'total': total})

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in items)

    # Create an order
    order = Order.objects.create(user=request.user, total_amount=total)
    for item in items:
        order.items.add(item.menu_item)
    order.save()

    # Clear the cart
    cart.cartitem_set.all().delete()

    return render(request, 'checkout.html', {'order': order})
