from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import datetime
from django.db.models import Avg
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from .forms import *
from .models import *
from openpyxl import Workbook
from django.contrib import messages
from django.db.models import Q


from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'base.html')


def delete_user(request, username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        user.delete()
        return HttpResponse(f"Пользователь {username} удалён.")
    except User.DoesNotExist:
        return HttpResponse("Пользователь не найден.")



#Корзина

@login_required
def add_to_card(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = CartItem.objects.get_or_create(
        product=product,
        user=request.user,
        defaults={'quantity':1}
    )
    if not created:
        item.quantity += 1
        item.save()
    return redirect('cart-view')

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = CartItem.objects.filter(user=self.request.user)
        total = sum([item.total_price() for item in items])
        context['cart_items'] = items
        context['total_price'] = total
        return context

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart-view')

@login_required
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return redirect('cart-view')


#Логика Акк.

class SignUpView(CreateView):
    model = Client
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

class SignInView(LoginView):
    template_name = 'registration/login.html'

class SignOutView(LogoutView):
    template_name = 'registration/login.html'

#Личный каб
@login_required
def profile_edit_view(request):
    user = request.user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профль Обновлен')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'profile_edit.html', {
        'form': form,
        'order': orders
    })

@login_required
def profile_view(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    user_products = None
        
    if request.user.role == 'seller':
        user_products = Product.objects.filter(seller=request.user)

    return render(request, 'profile.html', {
        'order': user_orders,
        'user_products': user_products,
    })

@login_required
def add_product_view(request):
    if request.user.role != 'seller':
        return redirect('profile')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.owner = request.user
            product.save()
            return redirect('profile')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    return redirect('profile')


@login_required
def account_settings_view(request):
    user = request.user
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AccountSettingsForm(instance=user)
    return render(request, 'account_settings.html', {'form': form})

#CRUD и вьюшка для продуктов

class ProductViewList(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        queryset = Product.objects.all()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    fields = ['title', 'description', 'price', 'category', 'image']
    template_name = 'product_form.html'
    success_url = reverse_lazy('product-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        return self.request.user.groups.filter(name='Продавец').exists()
    
class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['title', 'description', 'price', 'category', 'image']
    template_name = 'product_form.html'
    success_url = reverse_lazy('product-list')

    def test_func(self):
        product = self.get.object()
        return product.owner == self.request.user

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

    def test_func(self):
        product = self.get.object()
        return product.owner == self.request.user

@login_required
def leave_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        text = request.POST.get('text')
        rating = request.POST.get('rating', 5)
        Review.objects.create(user=request.user, product=product, text=text, rating=rating)
        return redirect('product-list')
    
    return render(request, 'leave_review.html', {'product': product})

def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.select_related('user').all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    return render(request, 'product_reviews.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating
    })

#Ордееррр

def create_exc_ord(Order):
    wb = Workbook()
    ws = wb.active
    ws.title = "Order Info"

    ws.append(["Информация о заказе"])
    ws.append(["ID заказ", Order.id])
    ws.append(["Юзер", Order.user.username])
    ws.append(["Дата заказа", Order.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(Order, 'created_at') else "N/A"])
    ws.append([])

    ws.append(["Product", "Quantity", "Price", "Total"])

    for item in Order.items.all():
        total = item.quantity * item.price
        ws.append([item.product.title, item.quantity, item.price, total])

    ws.append([])
    ws.append(["", "", "Итого:", sum(item.quantity * item.price for item in Order.items.all())])

    filename = f"order_{Order.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    from io import BytesIO
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    return filename, ContentFile(excel_file.read())


@login_required
def create_order(request):
    order = Order.objects.create(user=request.user)    
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items:
        return redirect('cart-view')


    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    filename, file_content = create_exc_ord(order)

    
    path = default_storage.save(f'notifications/{filename}', file_content)

    Notification_Order.objects.create(
        user=request.user,
        message=f"Ваш заказ №{order.id} успешно оформлен.",
        file=path
    )

    cart_items.delete()
    return render(request, 'order_success.html', {'order': order})


@login_required
def notif_list(request):
    notes = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notification.html', {'notifications': notes})