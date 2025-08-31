from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, CartItem

# ------------------------------
# Register
# ------------------------------
class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'ecommerceapp/registration/register.html'
    success_url = reverse_lazy('login')

# ------------------------------
# Login
# ------------------------------
class UserLoginView(LoginView):
    template_name = 'ecommerceapp/registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Logged in successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('product-list')  # or 'home' if you have a HomeView

# ------------------------------
# Logout
# ------------------------------
class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Logged out successfully!")
        return super().dispatch(request, *args, **kwargs)

# ------------------------------
# Products
# ------------------------------
class ProductListView(ListView):
    model = Product
    template_name = 'ecommerceapp/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

class ProductDetailView(DetailView):
    model = Product
    template_name = 'ecommerceapp/product_detail.html'
    context_object_name = 'product'

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_products'] = Product.objects.order_by('-id')[:8]
        if self.request.user.is_authenticated:
            context['latest_cart_items'] = CartItem.objects.filter(user=self.request.user).order_by('-id')[:4]
        else:
            context['latest_cart_items'] = []
        return context

# ------------------------------
# Cart
# ------------------------------
@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.stock < 1:
        messages.error(request, "Sorry, product is out of stock!")
        return redirect('product-detail', pk=pk)

    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} added to your cart!")
    return redirect('product-detail', pk=pk)

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from your cart!")
    return redirect('cart-view')

@login_required
def cart_view(request):
    items = CartItem.objects.filter(user=request.user)
    total = sum([item.subtotal() for item in items])
    return render(request, 'ecommerceapp/cart.html', {'items': items, 'total': total})
