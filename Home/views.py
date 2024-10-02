from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from .models import Tea, Order
from .forms import OrderForm

def tea_list(request):
    teas = Tea.objects.all()
    return render(request, 'tea_list.html', {'teas': teas})

def tea_detail(request, pk):
    tea = get_object_or_404(Tea, pk=pk)
    return render(request, 'tea_detail.html', {'tea': tea})

def order_tea(request, pk):
    tea = get_object_or_404(Tea, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.tea = tea
            order.save()
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request, 'order_tea.html', {'tea': tea, 'form': form})

def order_success(request):
    return render(request, 'order_success.html')
def index(request):
     return render(request,'home.html')
def login_user(request):
     return render(request,'login.html')