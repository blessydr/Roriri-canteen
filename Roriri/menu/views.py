from django.shortcuts import render, redirect,get_object_or_404
from .models import MenuItem, Cart, CartItem, Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


# Create Razorpay Order
def create_order(request):
    if request.method == 'POST':
        try:
            # Get the amount from POST data
            amount = int(request.POST.get('amount'))  # Amount in INR
            if amount <= 0:
                return JsonResponse({'error': 'Invalid amount'})

            # Create a Razorpay Order
            razorpay_order = razorpay_client.order.create({
                'amount': amount * 100,  # Convert to paise
                'currency': 'INR',
                'payment_capture': '1',  # Auto-capture payment
            })
            # Save the order in the database
            order = Order.objects.create(
                user=request.user,
                order_id=razorpay_order['id'],
                total_amount=amount,
            )

            # Render the payment page
            return render(request, 'payment_page.html', {
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount': amount * 100,  # Convert to paise
            })

        except Exception as e:
            return JsonResponse({'error': f"Order creation failed: {str(e)}"})

    return render(request, 'create_order.html')


# Handle Payment Success
@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        # Retrieve payment details from POST request
        payment_id = request.POST.get('razorpay_payment_id')
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        if not (payment_id and order_id and signature):
            return JsonResponse({'error': 'Missing payment details'})

        try:
            # Verify the Razorpay payment signature
            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            })

            # Update order status in the database
            order = Order.objects.get(order_id=order_id)
            order.payment_status = 'Completed'
            order.save()

            return render(request, 'payment_success.html', {'order': order})

        except razorpay.errors.SignatureVerificationError:
            return render(request, 'payment_failure.html', {
                'error': 'Payment verification failed. Please try again.'
            })

        except Order.DoesNotExist:
            return render(request, 'payment_failure.html', {
                'error': 'Order not found. Please contact support.'
            })

    return JsonResponse({'status': 'Invalid request'})


def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failure(request):
    return render(request, 'payment_failure.html')

from datetime import datetime

def menu_list(request):
    items = MenuItem.objects.all()

    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    category = request.GET.get('category', '')

    if search_query:
        items = items.filter(name__icontains=search_query)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            items = items.filter(created_at__gte=from_date_obj)
        except ValueError:
            pass

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            items = items.filter(created_at__lte=to_date_obj)
        except ValueError:
            pass 

    if category:
        items = items.filter(category=category)

    return render(request, 'menu.html', {'items': items})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user) 
            messages.success(request, 'Login successful!')
            return redirect('menu_list')  
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('user_login')  

    return render(request, 'login.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('user_login')  

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password)
        user.save()
        
        login(request, user)
        
        messages.success(request, 'Account created successfully!')
        return redirect('menu_list')  

    return render(request, 'register.html')

# def menu_list(request):
#     menu_items = MenuItem.objects.all()
#     return render(request, 'menu_list.html', {'menu_items': menu_items})
@login_required
def add_to_cart(request, item_id):
    item = MenuItem.objects.get(id=item_id)

    # Check if the item is in stock
    if item.stock > 0:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=item)
        
        if created:
            cart_item.quantity = 1  # Set initial quantity to 1
        else:
            cart_item.quantity += 1  # Increase quantity if already in the cart
        
        cart_item.save()

        # Reduce stock by 1 when an item is added to the cart
        item.stock -= 1
        item.save()

        messages.success(request, f'{item.name} added to cart.')
    else:
        messages.error(request, f'{item.name} is out of stock.')

    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    total = sum(item.total_price() for item in items)
    return render(request, 'cart_detail.html', {'items': items, 'total': total})

# @login_required
# def checkout(request):
#     cart = Cart.objects.get(user=request.user)
#     items = cart.cartitem_set.all()
#     total = sum(item.total_price() for item in items)

#     order = Order.objects.create(user=request.user, total_amount=total)
#     for item in items:
#         order.items.add(item.menu_item)
#     order.save()

#     cart.cartitem_set.all().delete()

#     return render(request, 'checkout.html', {'order': order})


@login_required
def remove_from_cart(request, item_id):
    cart = Cart.objects.get(user=request.user)
    cart_item = CartItem.objects.get(cart=cart, id=item_id)
    
    # Increase stock when item is removed from cart
    item = cart_item.menu_item
    item.stock += cart_item.quantity
    item.save()

    # Remove item from cart
    cart_item.delete()

    return redirect('cart_detail')


@login_required
def order_history(request):
    """
    Display the order history for the logged-in user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})