
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
@register.filter
def in_list(value, list_values):
    return value in list_values.split(',')
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def batch(iterable, batch_size):
  
    iterable = list(iterable)
    for i in range(0, len(iterable), batch_size):
        yield iterable[i:i + batch_size]
@register.filter
def format_weight(weight):
    """
    Converts weight in kg to grams if it's less than 1kg.
    Otherwise, display the weight in kilograms.
    """
    if weight < 1:
        # Convert kg to grams for weights less than 1kg
        return f"{weight * 1000:.0f} g"
    else:
        # Show weight in kilograms for weights equal to or greater than 1kg
        return f"{weight:.0f} kg"