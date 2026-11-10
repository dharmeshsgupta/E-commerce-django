from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductGallery
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct
from .models import ReviewRating
from django.urls import reverse
# Create your views here.

def store(request, category_slug=None):
    categories = None
    products = None
    category_links = Category.objects.all()
    
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
    context = {
        'products': paged_products,
        'product_count': product_count,
        'links': category_links,
    }
    return render(request, "store/store.html", context)


def product_detail(request, category_slug, product_slug):
    single_product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(user=request.user, product=single_product).exists()
    else:
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    
    try:
        if request.user.is_authenticated:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
        else:
            orderproduct = None
    except Exception:
        orderproduct = None
        orderproduct = None
        
    #Get The Reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    
    #Get The Product Gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, "store/product_detail.html", context)

def search(request):
    products = []
    product_count = 0
    category_links = Category.objects.all()
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(discription__icontains=keyword) | Q(product_name__icontains=keyword))
            paginator = Paginator(products, 6)  # Show 6 products per page
            page = request.GET.get('page')
            paged_products = paginator.get_page(page)
            product_count = products.count()
            products = paged_products # Overwrite products with the paginated version
    context = {
        'products': products,
        'product_count': product_count,
        'links': category_links,
    }
    return render(request, "store/store.html", context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated.')
                return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.ip = request.META.get('REMOTE_ADDR') # Get user's IP
                data.product_id = product_id
                data.user = request.user
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)