
from django import template
from django.utils.translation import gettext as _
import locale
register = template.Library()

@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''  #

def sum_price(cart_items):
    return sum(item.quantity * item.product.price for item in cart_items)
@register.filter
def total_cart_quantity(cart_items):
    total_quantity = sum(item.quantity for item in cart_items)
    return total_quantity


@register.filter
def currency(value):
    try:
        # Set locale for Indian Rupee formatting
        locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')  # Adjust for your locale
        return f"₹ {value:,.2f}"  # Format as currency in INR with rupee symbol
    except Exception as e:
        return str(value)