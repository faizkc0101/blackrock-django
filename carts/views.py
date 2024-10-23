from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from decimal import Decimal





def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Handling variations if any (add logic for variations as needed)
    product_variation = []

    if request.method == 'POST':
        # Example of handling product variations from form data
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except Variation.DoesNotExist:
                pass

    # For authenticated users
    if request.user.is_authenticated:
        user = request.user
        try:
            cart_item = CartItem.objects.get(user=user, product=product)
            # Check if the variations are the same; otherwise, create a new item
            existing_variation = cart_item.variations.all()
            if product_variation and list(existing_variation) == product_variation:
                cart_item.quantity += 1
                cart_item.save()
            else:
                
                cart_item = CartItem.objects.create(
                    user=user, 
                    product=product, 
                    quantity=1
                )
                if product_variation:
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                user=user, 
                product=product, 
                quantity=1
            )
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()
    
    # For anonymous users (session-based)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            existing_variation = cart_item.variations.all()
            if product_variation and list(existing_variation) == product_variation:
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = CartItem.objects.create(
                    cart=cart, 
                    product=product, 
                    quantity=1
                )
                if product_variation:
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart, 
                product=product, 
                quantity=1
            )
            if product_variation:
                cart_item.variations.add(*product_variation)
            cart_item.save()

    return redirect('cart_detail')  # Replace with the actual URL name of your cart detail page



def remove_cart(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass  # Handle item not found silently; consider logging for debugging

    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass  # Handle item not found silently; consider logging for debugging

    return redirect('cart')




def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        # Handle the exception (e.g., log it)
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)



@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_id=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (10 * total) / 100
        grand_total = total + tax
    except Cart.DoesNotExist:
        cart_items = []
    
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request,'store/checkout.html',context)