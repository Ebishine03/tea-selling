from django import forms
from .models import Address, Payment,Review
from Home .models import CustomUser
from Products .models import Delivery
class CheckoutForm(forms.Form):
    address = forms.ModelChoiceField(queryset=Address.objects.none(), required=True, label="Select Address")
    phone_number = forms.CharField(max_length=15, required=True, label="Phone Number")
    payment_method = forms.ChoiceField(choices=[('credit_card', 'Credit Card'), ('paypal', 'PayPal')], required=True)
    card_number = forms.CharField(max_length=16, required=False, label="Card Number")
    expiration_date = forms.CharField(max_length=5, required=False, label="Expiration Date (MM/YY)")
    cvv = forms.CharField(max_length=3, required=False, label="CVV")
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = Address.objects.filter(user=user)


class DeliveryInfoForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['full_name', 'phone_number','home', 'street', 'city', 'state', 'pin_code', 'country']
        widgets = {
             'home': forms.TextInput(attrs={'placeholder': 'Home '}),
            'street': forms.TextInput(attrs={'placeholder': 'Street Address'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'placeholder': 'State'}),
            'pin_code': forms.TextInput(attrs={'placeholder': 'Pin Code'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
        }
class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, label="Quantity")

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, str(i)) for i in range(1, 6)],  
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Write your review here...'
                }
            ),
        }
        labels = {
            'rating': 'Rate the Product',
            'comments': 'Your Review',
        }
