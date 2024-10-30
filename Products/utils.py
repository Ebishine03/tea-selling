# your_app/utils.py

def calculate_delivery_charge(order):
    if order.total_weight <= 5:
        return 5.00  # Flat rate for up to 5kg
    elif order.total_weight <= 10:
        return 10.00  # Increased rate for 6-10kg
    else:
        return 15.00  # Maximum rate for over 10kg
