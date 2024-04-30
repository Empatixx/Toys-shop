from datetime import timedelta, datetime

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now

from .models import Product, Order, User, Category, OrderProduct, OrderState, Review


def register(request):
    if request.method == 'POST':

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        telephone = request.POST.get('telephone')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if username := request.POST.get('username'):
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username is already taken.')
                return redirect('register')

        if not username or not first_name or not last_name or not address or not city or not telephone:
            messages.error(request, 'All fields are required.')
            return redirect('register')

        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                        address=address, telephone=telephone, city=city, role="C", password=password1)
        login(request, user)
        return redirect('home')
    return render(request, 'registration/register2.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        request.user.telephone = request.POST.get('telephone')
        request.user.address = request.POST.get('address')
        request.user.city = request.POST.get('city')
        request.user.save()
        messages.success(request, 'Profile updated successfully.')
    return render(request, 'profile/profile.html', {
        'user': request.user,
        'cart_item_count': sum(request.session.get('cart', {}).values())
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if not form.is_valid():
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

        login(request, form.get_user())
        return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login/login2.html', {'form': form})


def products(request):
    category_list = Category.objects.all()
    selected_category = request.GET.get('selected_category', None)
    search_query = request.GET.get('search_query', None)

    products = Product.objects.all()

    if selected_category and search_query:
        products = (products.filter(category__id=selected_category, name__icontains=search_query)
                    .prefetch_related('review_set')
                    .order_by('deleted', 'price'))
    elif selected_category:
        products = (products.filter(category__id=selected_category)
                    .prefetch_related('review_set')
                    .order_by('deleted', 'price'))
    elif search_query:
        products = (Product.objects.filter(name__icontains=search_query)
                    .prefetch_related('review_set')
                    .order_by('deleted', 'price'))
    else:
        products = (products.order_by('price')
                    .prefetch_related('review_set')
                    .order_by('deleted', 'price'))
    return render(request, 'products/products2.html', {
        'category_list': category_list,
        'product_list': products,
        'cart_item_count': sum(request.session.get('cart', {}).values()),
        'current_page': 'products',
        'selected_category': selected_category
    })


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    request.session['cart'] = cart
    messages.success(request, 'Product added to cart.')
    return redirect('products')


def view_cart(request):
    cart = request.session.get('cart', {})

    products = Product.objects.filter(id__in=cart.keys())

    cart_items = {}
    total_items = 0
    total_price = 0

    for product in products:
        quantity = cart[str(product.id)]
        total_price_product = product.price * quantity

        cart_items[product] = {
            'quantity': quantity,
            'total_price': total_price_product
        }

        total_items += quantity
        total_price += total_price_product

    for product_id in list(cart.keys()):
        if not Product.objects.filter(id=product_id).exists():
            cart.pop(product_id)
    request.session['cart'] = cart
    request.session.modified = True

    return render(request, 'products/view_cart.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'cart_item_count': total_items,
        'total_price': total_price,
        'total_amount': total_price,
        'delivery_date': now().date() + timedelta(days=7),
        'current_page': 'products'
    })


from django.shortcuts import redirect


def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_quantity = int(request.POST.get('quantity', 1))

        if new_quantity > 0:
            request.session['cart'][product_id] = new_quantity
        else:
            request.session['cart'].pop(product_id, None)

        request.session.modified = True
        return redirect('view_cart')

    return redirect('view_cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
    messages.success(request, 'Product removed from cart.')
    return redirect('view_cart')


def orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.role is 'C':
        order_list = Order.objects.filter(customer=request.user).prefetch_related('orderproduct_set').order_by(
            '-expected_delivery')
    else:
        messages.error(request, "You must be a customer to access this page.")
        return redirect('home')
    return render(request, 'orders/orders.html', {
        'orders': order_list,
        'cart_item_count': sum(request.session.get('cart', {}).values()),
        'current_page': 'orders'
    })


def manage_employees(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_manager():
        messages.error(request, "You must be a manager to access this page.")
        return redirect('home')
    search_query = request.GET.get('search_query', '').strip()
    if search_query:
        employees = User.objects.filter(username__icontains=search_query).filter(role='S')
    else:
        employees = User.objects.all().filter(role='S')
    return render(request, 'manage_employees/manage_employees.html', {
        'employees': employees,
        'current_page': 'manage_employees'
    })


def delete_employee(request, employee_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_manager():
        messages.error(request, "You must be a manager to delete an employee.")
        return redirect('home')
    if request.method == 'POST':
        employee = get_object_or_404(User, pk=employee_id)
        employee.delete()
        return redirect("manage_employees")
    return redirect("manage_employees")


def edit_employee(request, employee_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_manager():
        messages.error(request, "You must be a manager to edit an employee.")
        return redirect('home')

    employee = get_object_or_404(User, pk=employee_id)
    if request.method == 'POST':
        employee.username = request.POST.get('username')
        employee.telephone = request.POST.get('telephone')
        employee.address = request.POST.get('address')
        employee.city = request.POST.get('city')
        employee.save()
    return redirect("manage_employees")


def manage_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    orders = Order.objects.all().select_related('customer').prefetch_related('orderstate_set').prefetch_related(
        "orderproduct_set").order_by('-expected_delivery')
    return render(request, 'manage_orders/manage_orders2.html', {
        'orders': orders,
        'current_page': 'manage_orders'
    })


def manage_categories(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    search_query = request.GET.get('search_query', '').strip()
    if search_query:
        categories = Category.objects.filter(name__icontains=search_query)
    else:
        categories = Category.objects.all()

    return render(request, 'manage_categories/manage_categories2.html', {
        'categories': categories,
        'current_page': 'manage_categories'
    })


def add_product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('productName')
        description = request.POST.get('description')
        price = request.POST.get('price')
        amount_left = request.POST.get('amount_left')
        category = request.POST.get('category')
        new_product = Product(name=name, description=description, price=price,
                              amount_left=amount_left, category=Category.objects.get(id=category),
                              employee=request.user)
        new_product.save()
        return redirect('products')
    return redirect('products')


def create_category(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        if name and description:
            Category.objects.create(name=name, description=description)
            return redirect('manage_categories')
        else:
            return HttpResponse("Both name and description are required.", status=400)

    return redirect('manage_categories')


def edit_category(request, category_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name and description:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, "Category updated successfully.")
            return redirect('manage_categories')
        else:
            messages.error(request, "Both name and description are required.")
            return redirect('manage_categories')
    return redirect('manage_categories')


def delete_category(request, category_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect('manage_categories')
    return redirect('manage_categories')


def delete_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    if request.method == 'POST':  # Ensure this is a POST request
        product = get_object_or_404(Product, pk=product_id)
        product.deleted = True
        product.save()
        messages.success(request, "Product deleted successfully.")
        return redirect("products")
    return redirect("products")


def edit_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        print(request.POST)
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.amount_left = request.POST.get('amount_left')
        product.category = Category.objects.get(id=request.POST.get('category'))
        product.save()
        messages.success(request, "Product updated successfully.")
    return redirect("products")


def increase_cart_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    cart[product_id] += 1
    request.session['cart'] = cart
    return redirect('view_cart')


def decrease_cart_quantity(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)
    if cart[product_id] > 1:
        cart[product_id] -= 1
    else:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('view_cart')


def order_details(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == 'C':
        order = Order.objects.get(id=order_id)
        if order.customer != request.user:
            messages.error(request, "You don't have permission to view this order.")
            return redirect('orders')
    order = Order.objects.get(id=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    return render(request, 'orders/order_details.html', {
        'order': order,
        'order_products': order_products,
        'cart_item_count': sum(request.session.get('cart', {}).values()),
        'current_page': 'orders'
    })


def create_order(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        customer = request.user
        if not customer.is_authenticated:
            messages.error(request, "You must be logged in to create an order.")
            return redirect('login')
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Your cart is empty.")
            return redirect('view_cart')
        if not customer.address or not customer.city:
            messages.error(request, "Please update your address and city in your profile.")
            return redirect('profile')
        if not customer.telephone:
            messages.error(request, "Please update your telephone number in your profile.")
            return redirect('profile')

        products = Product.objects.filter(id__in=cart.keys())
        for product in products:
            if cart[str(product.id)] > product.amount_left:
                messages.error(request, f"Product {product.name} has only {product.amount_left} left in stock.")
                return redirect('view_cart')

        order = Order.objects.create(
            customer=customer,
            address=customer.address,
            city=customer.city,
            state='Pending',
            expected_delivery=datetime.now() + timedelta(days=3)
        )

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderProduct.objects.create(
                order=order,
                product=product,
                amount=quantity,
                price_per=product.price
            )

        state = OrderState.objects.create(order=order, state='Pending', created_at=now())

        request.session['cart'] = {}
        request.session.modified = True

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            product.amount_left -= quantity
            product.save()

        return redirect('order_details', order_id=order.id)

    return redirect('view_cart')


def delete_order(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        order.delete()
        return redirect("manage_orders")
    return redirect("manage_orders")


def edit_order(request, order_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_product_manager():
        messages.error(request, "You must be a product manager to access this page.")
        return redirect('home')

    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        if not request.POST.get('orderState'):
            messages.error(request, "Order state is required.")
            return redirect('manage_orders')
        order.state = request.POST.get('orderState')
        order.save()

        OrderState.objects.create(order=order, state=order.state, created_at=now())
        messages.success(request, "Order updated successfully.")
    return redirect("manage_orders")


def create_employee(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_manager():
        messages.error(request, "You must be a manager to access this page.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        telephone = request.POST.get('telephone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = 'S'

        if username == request.user.username:
            messages.error(request, "You can't create an employee with the same username as yours.")
            return redirect('manage_employees')

        # generate
        password = User.objects.make_random_password()

        customer = User.objects.filter(username=username)
        if customer:
            messages.info(request, "Username already exists. Converting to employee.")
            customer = customer[0]
            customer.role = role
            customer.save()
            messages.success(request, "Employee created successfully. Password: " + password)
            return redirect('manage_employees')

        if username and telephone and address and city and first_name and last_name:
            User.objects.create(username=username,  telephone=telephone, address=address, city=city,
                                role=role, password=password)
            messages.success(request, "Employee created successfully. Password: " + password)
            return redirect('manage_employees')
        else:
            messages.error(request, "All fields are required.")
    return redirect('manage_employees')


def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    category_list = Category.objects.all()
    return render(request, 'products/product_details.html', {
        'product': product,
        'category_list': category_list,
        'cart_item_count': sum(request.session.get('cart', {}).values()),
        'current_page': 'products'
    })


def review(request, product_id):
    product = Product.objects.get(id=product_id)
    return render(request, 'review/review.html', {
        'product': product,
        'cart_item_count': sum(request.session.get('cart', {}).values()),
        'current_page': 'products'
    })


def create_review(request, product_id):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        review_text = request.POST.get('review_text')
        rating = request.POST.get('rating')
        if not review_text or not rating:
            messages.error(request, "Review text and rating are required.")
            return redirect('review', product_id=product_id)
        Review.objects.create(review_text=review_text, rating=rating, created_at=now(), product=product,
                              customer=request.user)
        return redirect('product_details', product_id=product_id)
    return redirect('review', product_id=product_id)
