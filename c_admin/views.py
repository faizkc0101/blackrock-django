from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import Account
from store.models import Product, Variation
from category.models import Category

# Login view
def c_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('c_dashboard')
        messages.error(request, 'Invalid credentials or no admin privileges')
    return render(request, 'c_admin/c_login.html')


@login_required
def c_dashboard(request):
    return render(request, 'c_admin/c_dashboard.html')

# Manage users
@login_required
def c_users(request):
    users = Account.objects.all()
    return render(request, 'c_admin/c_users.html', {'users': users})

@login_required
def user_status(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    user.is_active = not user.is_active
    user.save()
    return redirect('c_users')

# Product management
@login_required
def c_products(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    variations = Variation.objects.all()
    return render(request, 'c_admin/c_products.html', {
        'products': products, 
        'categories': categories, 
        'variations': variations
    })

@login_required
def toggle_availability(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.is_available = not product.is_available
    product.save()
    return redirect('c_products')

@login_required
def c_add_product(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        product = Product(
            product_name=request.POST['product_name'],
            slug=request.POST['slug'],
            description=request.POST['description'],
            price=request.POST['price'],
            images=request.FILES.get('images'),
            stock=request.POST['stock'],
            is_available='is_available' in request.POST,
            category_id=request.POST['category'],
        )
        product.save()
        return redirect('c_products')
    return render(request, 'c_admin/c_add_product.html', {'categories': categories})

@login_required
def c_update_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.product_name = request.POST['product_name']
        product.slug = request.POST['slug']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.is_available = 'is_available' in request.POST
        product.category_id = request.POST['category']
        if request.FILES.get('images'):
            product.images = request.FILES['images']
        product.save()
        return redirect('c_products')
    return render(request, 'c_admin/c_update_product.html', {'product': product, 'categories': categories})

@login_required
def c_delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    product.delete()
    return redirect('c_products')

# Category management
@login_required
def c_add_category(request):
    if request.method == 'POST':
        category = Category(
            category_name=request.POST['category_name'],
            slug=request.POST['slug'],
        )
        category.save()
        return redirect('c_products')
    return render(request, 'c_admin/c_add_category.html')

@login_required
def c_update_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        category.category_name = request.POST['category_name']
        category.slug = request.POST['slug']
        category.save()
        return redirect('c_products')
    return render(request, 'c_admin/c_update_category.html', {'category': category})

@login_required
def c_delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('c_products')

# Variation management
@login_required
def c_add_variation(request):
    products = Product.objects.all()
    if request.method == 'POST':
        variation = Variation(
            product_id=request.POST['product'],
            variation_category=request.POST['variation_category'],
            variation_value=request.POST['variation_value'],
            is_active='is_active' in request.POST,
        )
        variation.save()
        return redirect('c_products')
    return render(request, 'c_admin/c_add_variation.html', {'products': products})

@login_required
def c_update_variation(request, id):
    variation = get_object_or_404(Variation, id=id)
    products = Product.objects.all()
    if request.method == 'POST':
        variation.product_id = request.POST['product']
        variation.variation_category = request.POST['variation_category']
        variation.variation_value = request.POST['variation_value']
        variation.is_active = 'is_active' in request.POST
        variation.save()
        return redirect('c_products')
    return render(request, 'c_admin/c_update_variation.html', {'variation': variation, 'products': products})

@login_required
def c_delete_variation(request, id):
    variation = get_object_or_404(Variation, id=id)
    variation.delete()
    return redirect('c_products')
