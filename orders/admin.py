from django.contrib import admin
from .models import Payment, Order, OrderProduct
# Register your models here.


# This allows you to view products inside the Order page in Admin
class OrderProductInline(admin.TabularInline):
    model = OrderProduct  # Uncomment if you have an OrderProduct model
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    # Which columns to show in the list
    list_display = ['order_number', 'full_name', 'phone', 'email', 'city', 'order_total', 'tax', 'status', 'is_ordered', 'created_at']
    
    # Add filters on the right side
    list_filter = ['status', 'is_ordered']
    
    # Add a search bar
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    
    # Items per page
    list_per_page = 20
    
    # (OPTIONAL) Makes the 'status' dropdown editable directly from the list view!
    list_editable = ['status'] 

    # inlines = [OrderProductInline] # Uncomment if using OrderProduct

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)