from django.shortcuts import render, redirect,get_object_or_404
from .models import MenuItem, Cart, CartItem, Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
import razorpay
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.core.paginator import Paginator
import json
from django.forms import ValidationError
from django.views import View



def get_razorpay_client():
    """Returns the razorpay client."""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY) )

def is_razorpay_payment_order_successful(order_id):
    order_response = get_razorpay_client().order.fetch(order_id=order_id)
    return order_response.get("status") in ["paid"]

def create_razorpay_payment_order(amount, currency, receipt):
    return get_razorpay_client().order.create(
        data={
            "amount": int(int(amount) * 100),  # amount in paise
            "currency": currency,
            "receipt": receipt,
        }
    )

class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            amount = data.get("amount")
            currency = data.get("currency", "INR")
            receipt = data.get("receipt")
            order = create_razorpay_payment_order(amount, currency, receipt)
            return JsonResponse(order)
        except Exception as e:
            return JsonResponse({"error": str(e)})\
                
                

class VerifyPaymentView(View):
    def post(self, request, *args, **kwargs):
        try:
            # Parse JSON data from the request
            data = json.loads(request.body)
            payment_id = data.get("razorpay_payment_id")
            order_id = data.get("razorpay_order_id")
            signature = data.get("razorpay_signature")
            amount = data.get("amount")
            items = data.get("items")  # List of purchased item IDs
            user_id = data.get("user_id")

            # Verify Razorpay payment signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature,
            }
            get_razorpay_client.utility.verify_payment_signature(params_dict)

            # Create or update the order
            user = get_object_or_404(User, id=user_id)
            order = Order.objects.create(
                user=user,
                order_id=order_id,
                total_amount=amount,
                status="Completed"
            )
            for item_id in items:
                item = get_object_or_404(MenuItem, id=item_id)
                order.items.add(item)

            return JsonResponse({"status": "success", "message": "Payment verified and order saved."})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error": "Payment verification failed"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        
def payment_form(request):
    return render(request, 'menu.html', {
        'RAZORPAY_KEY_ID': settings.RAZORPAY_KEY_ID
    })

from datetime import datetime

def menu_list(request):
    items = MenuItem.objects.all()

    search_query = request.GET.get('search', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    category = request.GET.get('category', '')

    if search_query:
        items = items.filter(name__icontains=search_query)
    
    if from_date and to_date:
        items = items.filter(created_at__date__range=[from_date, to_date])

    if category:
        items = items.filter(category__iexact=category) 
        
                
    paginator = Paginator(items, 6)  # Show 6 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'menu.html',{'items': page_obj, 'page_obj': page_obj})


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



def generate_invoice(request, order_id):
    try:
        # Order details fetch pannunga
        order = Order.objects.get(order_id=order_id, user=request.user)

        # HTTP response setup for PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_id}.pdf"'

        # PDF canvas start
        buffer = canvas.Canvas(response, pagesize=A4)
        buffer.setFont("Helvetica", 12)

        # Document content write
        buffer.drawString(100, 800, "Invoice")
        buffer.drawString(100, 780, f"Order ID: {order.order_id}")
        buffer.drawString(100, 760, f"Customer: {order.user.username}")
        buffer.drawString(100, 740, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")

        # Snack details iterate & write
        y = 720
        buffer.drawString(100, y, "Items:")
        y -= 20
        for item in order.items.all():  # Assuming ManyToMany relation with MenuItem
            buffer.drawString(120, y, f"- {item.name} (₹{item.price})")
            y -= 20

        buffer.drawString(100, y - 20, f"Total Amount: ₹{order.total_amount}")

        # Close PDF
        buffer.showPage()
        buffer.save()

        return response

    except Order.DoesNotExist:
        return HttpResponse("Order not found.", status=404)

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

@login_required
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in items)

    order = Order.objects.create(user=request.user, total_amount=total)
    for item in items:
        order.items.add(item.menu_item)
    order.save()

    cart.cartitem_set.all().delete()

    return render(request, 'checkout.html', {'order': order})


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