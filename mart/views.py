from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.models import Group
from . utils import *
import json
from django.http import JsonResponse
import datetime


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    

    products = Product.objects.all()
    context = {'products':products, 'cartItems': cartItems}
    return render(request, "Store/store.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']   

    context = {'items': items, 'order': order, 'cartItems': cartItems }
    return render(request, "Store/cart.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def checkout(request):   
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']   

    context = {'items': items, 'order': order, 'cartItems': cartItems }
    
    return render(request, "Store/checkout.html", context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created =OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem. quantity -1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()        
    return JsonResponse('Item was added', safe=False)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer, complete=False)
        
    
        
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
            order.save()
           

        if order.shipping == True:
                ShippingAddress.objects.create(
                    customer=customer,
                    order=order,
                    address=data['shipping']['address'],
                    city=data['shipping']['city'],
                    state=data['shipping']['state'],
                    zipcode=data['shipping']['zipcode'],
                )

    return JsonResponse('Payment complete', safe=False)


@unauthenticated_user
def loginPage(request):

    
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
               login(request, user)
               return redirect('home')
        else:
              messages.info(request, 'username or password is incorrect')

    context = {}
    return render(request, 'account/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@unauthenticated_user
def registerPage(request):
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid(): 
                #saving the registered user
                user = form.save()
                Customer.objects.create(
                    user = user,
                    name = user.username,
                    email = user.email
                )    
                username= form.cleaned_data.get('username')
                group = Group.objects.get(name='customer')
                user.groups.add(group)
 
                messages.success(request, f'Your Account has been created! You can now log in')
                return redirect('login')
        else:
            form = UserCreationForm() #creates an empty form
        return render(request, 'account/register.html', {'form': form})


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def settingPage(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context = {'form': form}
    return render(request, 'account/settings.html', context)

   

@login_required(login_url='login')
@admin_only
def home(request):
    orders = Order.objects.all()
    
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    context = {
        'orders': orders, 'customers': customers, 'total_orders': total_orders, 'delivered': delivered,
        'pending': pending
        }

    return render(request, 'account/dashboard.html', context)

   

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    print('ORDERS:', orders)
    context = {
        'orders': orders, 'total_orders': total_orders, 'delivered': delivered,
        'pending': pending
        }
    return render(request, 'account/user.html', context)     

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    context = {
        "products": products
    }
    return render(request, 'account/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
    customer = Customer.objects.get(id=pk_test)
    orders = customer.order_set.all()
    order_count = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {
        'customer': customer, 'orders': orders, 'order_count': order_count, 'myFilter': myFilter,
        
    }
    return render(request, 'account/customer.html', context) 

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('Product', 'status'), extra=20)
    
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet( queryset=Order.objects.none(), instance=customer)
    #form = OrderForm()
    if request.method == 'POST':
       # form = OrderForm(request.POST)
       formset = OrderFormSet(request.POST, instance=customer)
       if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset': formset}    
    return render(request, 'account/order_form.html',context)
  

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request, pk):
 
    order = Order.objects.get(id=pk)
    formset = OrderForm( instance=order)

    if request.method =='POST':
        formset = OrderForm(request.POST, instance=order)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    context = {'formset': formset}
    return render(request, 'account/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request, pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()   
        return redirect('/') 
    context = {'item': order}  
    return render(request, 'account/delete_form.html', context)    



