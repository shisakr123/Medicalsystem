from django.shortcuts import render, redirect
from .models import Customer, Product, Order
from .filters import ProductFilter
from .forms import Form, ProductForm, ContactForm
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def dashboard(request):
    orders = Order.objects.all()
    orders_label = set()
    for o in orders:
        orders_label.add(o.product)
    orders_group = list(Order.objects.values('product').annotate(dcount=Count('product')))
    og = []
    for o in orders_group:
        og.append(o["dcount"])
    total_orders = orders.count()
    recent_orders = orders.order_by('-date_created')[:5]
    context  = {'orders': orders, 'orders_label': orders_label, 'products': products,
    'total_orders':total_orders, 'recent_orders':recent_orders,'og':og}
    return render(request,'crm/dashboard.html', context)


def products(request):
    products = Product.objects.all()
    pf = ProductFilter(request.GET, queryset=products)
    products = pf.qs
    return render(request,'crm/products.html',{'products':products,'pf':pf})


def delete_product(request, pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def update_product(request, pk):
    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)
    if request.method == 'POST':
        form = ProductForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
            return redirect('/products')
    context = {'form': form}
    return render(request,'crm/form_page.html',context)


def create_product(request):
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/products')
    context = {'form':form}
    return render(request,'crm/form_page.html', context)


def orders(request):
    orders = Order.objects.order_by("-date_created")
    return render(request,'crm/orders.html',{'orders':orders})


def contacts(request):
    req = request.GET.get('search',None)
    if req is not None:
        query = request.GET.get('search')
        customers = Customer.objects.filter(Q(name__icontains=query) | Q(email__icontains=query)
        | Q(phone__icontains=query)
        | Q(address__icontains=query))
    else:
        customers = Customer.objects.all()
    return render(request,'crm/contacts.html',{'customers':customers})


def add_contact(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/contacts')
    context = {'form':form}
    return render(request,"crm/form_page.html",context)


def update_contact(request, pk):
    contact = Customer.objects.get(id=pk)
    form = ContactForm(instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST,instance=contact)
        if form.is_valid():
            form.save()
            return redirect('/contacts')
    context = {'form': form}
    return render(request,'crm/form_page.html',context)


def delete_contact(request, pk):
    contact = Customer.objects.get(id=pk)
    contact.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def customer_orders(request, pk):
    customer = Customer.objects.get(id=pk)
    order = customer.order_set.all()
    total_orders = order.count()
    context = {'customer':customer,'order':order, 'total_orders':total_orders}
    return render(request,'crm/customer_orders.html', context)


def create_order(request):
    form = Form()
    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/orders')
    context = {'form':form}
    return render(request,'crm/form_page.html', context)


def update_order(request, pk):
    order = Order.objects.get(id=pk)
    form = Form(instance=order)
    if request.method == 'POST':
        form = Form(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('/orders')
    context = {'form': form}
    return render(request,'crm/form_page.html',context)
    

def delete_order(request, pk):
    order = Order.objects.get(id=pk)
    order.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            a=Customer.objects.get(email=username)
            if a:
                print(a.password)
                if a.password == password:
                    return redirect('home')
                else:
                    messages.info(request,"Password is not correct")
        except Customer.DoesNotExist:
            messages.info(request,"Username is not correct.")
    return render(request, 'crm/signin.html',{})

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_again = request.POST.get('password_again')
        email = request.POST.get('email')
        if password == password_again:
            Customer(name=username, password=password, email=email).save()
            return redirect('home')
        else:
            messages.info(request,"Username or Password is not correct.")
    return render(request, 'crm/signup.html',{})

def signout(request):
    logout(request)
    return redirect('signin')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_again = request.POST.get('password_again')
        if password == password_again:
            c=Customer.objects.get(email=email)
            c.password=password
            c.save()
            return redirect('signup')
        else:
            messages.info(request, "Username or Password is not correct.")
    return render(request, 'crm/forgot_password.html', {})

def checkout(request,id):
    order=Order.objects.get(id=id)
    return render(request,'crm/checkout.html',{'order':order})