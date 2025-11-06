from django.contrib import admin
from .models import Customer, Item, Bill, BillItem


#  Inline Bill Items (to show inside Bill admin)
class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1
    readonly_fields = ("total", "gst_amount")


#  Bill Admin
@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "date", "total_amount", "gst_amount", "net_amount")
    list_filter = ("date",)
    search_fields = ("customer_name",)
    inlines = [BillItemInline]


#  Item Admin
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "hsn_code", "price", "gst_rate", "stock")
    search_fields = ("name", "hsn_code")
    list_filter = ("gst_rate",)
    ordering = ("id",)


#  Customer Admin
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "gstin")
    search_fields = ("name", "phone", "gstin")
