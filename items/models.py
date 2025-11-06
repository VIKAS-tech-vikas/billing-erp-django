from django.db import models
from django.utils import timezone


# 👤 Customer Model
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    gstin = models.CharField(max_length=15, blank=True, null=True, default="NA")

    def __str__(self):
        return self.name


# 📦 Item Model
class Item(models.Model):
    name = models.CharField(max_length=200)
    alias = models.CharField(max_length=200, blank=True, null=True)
    group = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    purchase_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    opening_stock_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    hsn_code = models.CharField(max_length=50, blank=True, null=True, default="NA")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.hsn_code})"


# 🧾 Bill Model
class Bill(models.Model):
    customer_name = models.CharField(max_length=100, default="Walk-in Customer")
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Bill #{self.id} - {self.customer_name}"

    class Meta:
        ordering = ['-date']


# 📋 Bill Item Model
class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} × {self.quantity}"

    class Meta:
        verbose_name = "Bill Item"
        verbose_name_plural = "Bill Items"
        ordering = ['id']


# 🧾 Estimate Bill Model
class EstimateBill(models.Model):
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Estimate #{self.id} - {self.customer_name}"

    class Meta:
        ordering = ['-date']


# 📋 Estimate Item Model
class EstimateItem(models.Model):
    estimate = models.ForeignKey(EstimateBill, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} × {self.quantity}"

    class Meta:
        verbose_name = "Estimate Item"
        verbose_name_plural = "Estimate Items"
        ordering = ['id']

class CustomerPayment(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)  # ✅ Added properly

    def __str__(self):
        return f"{self.customer_name} - ₹{self.amount}"


