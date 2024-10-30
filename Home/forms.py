from django import forms

from .models import CustomUser,EmployeeProfile
from django.contrib.auth import get_user_model
from Products .models import Product,Order,Address
class CustomUserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number']  

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.role = 'customer'  
        if commit:
            user.save()
        return user

User = get_user_model()

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']  


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': 'required'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required'
        })
    )
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'description', 'price', 'stock', 'product_image','is_offer']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_offer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Correct Checkbox widget

            'product_image': forms.ClearableFileInput(attrs={'class': 'custom-file-input'}),  # Updated class
        }
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
           
        }

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone_number']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),

        }
            # 'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
           


class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        fields = ['image', 'date_hired', 'employee_type']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [  'street', 'city', 'state', 'pin_code', 'country']