from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    
    try:
        if request.user.is_authenticated:
            # For authenticated users
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            # For anonymous users
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
        
        
        for item in cart_items:
            cart_count += item.quantity
    
    except Cart.DoesNotExist:
        cart_count = 0
    
    return {'cart_count': cart_count}
