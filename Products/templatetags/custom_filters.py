
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''  #
@register.filter
def sum_price(cart_items):
    return sum(item.quantity * item.product.price for item in cart_items)
@register.filter
def total_cart_quantity(cart_items):
    total_quantity = sum(item.quantity for item in cart_items)
    return total_quantity