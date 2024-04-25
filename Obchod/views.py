from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Product, Order, User, Category


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields  # Default fields (username, password1, password2)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Redirect to a success page.
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')  # Redirect to a home page or some other page
    else:
        form = AuthenticationForm()
    return render(request, 'login/login.html', {'form': form})


def home(request):
    return render(request, 'home.html')

def products(request):
    product_list = Product.objects.all()
    categories = Category.objects.all()
    print(categories)
    return render(request, 'products/products.html', {'product_list': product_list, 'category_list': categories})

def orders(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Replace 'login' with the name of your login route

    # Check if the user has the role of a customer (or whatever roles can have orders)
    if request.user.role == 'C':
        order_list = Order.objects.filter(customer=request.user).prefetch_related('orderproduct_set')
    else:
        order_list = []  # If not a customer, return an empty list

    return render(request, 'orders/orders.html', {'order_list': order_list})
def manage_employees(request):
    # Logic to fetch and manage employees
    return render(request, 'manage_employees/manage_employees.html')

def manage_orders(request):
    # Logic to fetch and manage orders
    return render(request, 'manage_orders/manage_orders.html')

def manage_categories(request):
    # Logic to fetch and manage orders
    categories = Category.objects.all()
    return render(request, 'manage_categories/manage_categories.html', {'categories': categories})

def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('productName')
        description = request.POST.get('description')
        price = request.POST.get('price')
        amount_left = request.POST.get('amount_left')
        category = request.POST.get('category')
        new_product = Product(name=name, description=description, price=price,
                              amount_left=amount_left, category=Category.objects.get(id=category), employee=request.user)
        new_product.save()
        print(new_product)
        return redirect('products')
    return render(request, 'products')  # Or wherever you want to redirect


def create_category(request):
    if request.method == 'POST':
        # Extracting data from POST request using the name attributes
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Check if both fields are filled
        if name and description:
            Category.objects.create(name=name, description=description)
            return redirect('manage_categories')  # Redirect to the category management page
        else:
            # Handle the error if necessary fields are missing
            return HttpResponse("Both name and description are required.", status=400)

    # Redirect back to the form page or handle accordingly if it's not a POST request
    return redirect('manage_categories')


def delete_product(request, product_id):
    if request.method == 'POST':  # Ensure this is a POST request
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return redirect("products")
    return redirect("products")


def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.amount_left = request.POST.get('amount_left')
        product.save()
    return redirect("products")