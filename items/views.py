from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.db.models import Q, Sum, Value as V, DecimalField
from django.db.models.functions import Coalesce
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Bill, EstimateBill, CustomerPayment
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from .models import Item, Bill, BillItem, EstimateBill, EstimateItem


# 🧩 LOGIN VIEW
# 🧩 LOGIN VIEW
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {username} 👋")
            # ✅ Redirect user to "Add Item" page after login
            return redirect("add_item")
        else:
            messages.error(request, "❌ Invalid username or password")
            return redirect("login_view")

    return render(request, "items/login.html")


# 🚪 LOGOUT VIEW
def logout_view(request):
    logout(request)
    messages.success(request, "✅ You have logged out successfully.")
    return redirect("login_view")


# 🟢 ADD ITEM VIEW
@login_required(login_url='login_view')
def add_item(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            messages.error(request, "⚠️ Product name is required!")
            return redirect("add_item")

        alias = request.POST.get("alias")
        group = request.POST.get("group")
        unit = request.POST.get("unit")
        purchase_price = request.POST.get("purchase_price")
        mrp = request.POST.get("mrp")
        sale_discount = request.POST.get("sale_discount")
        purchase_discount = request.POST.get("purchase_discount")
        description = request.POST.get("description")
        hsn_code = request.POST.get("hsn_code")
        price = request.POST.get("price")
        gst_rate = request.POST.get("gst_rate")
        stock = request.POST.get("stock")

        existing_item = Item.objects.filter(name__iexact=name).first()

        if existing_item:
            existing_item.stock += int(stock or 0)
            existing_item.price = float(price or existing_item.price)
            existing_item.gst_rate = float(gst_rate or existing_item.gst_rate)
            existing_item.unit = unit or existing_item.unit
            existing_item.mrp = float(mrp or existing_item.mrp)
            existing_item.purchase_price = float(purchase_price or existing_item.purchase_price)
            existing_item.sale_discount = float(sale_discount or existing_item.sale_discount)
            existing_item.purchase_discount = float(purchase_discount or existing_item.purchase_discount)
            existing_item.description = description or existing_item.description
            existing_item.hsn_code = hsn_code or existing_item.hsn_code
            existing_item.save()
            messages.success(request, f"✅ Existing item '{name}' updated successfully!")
        else:
            Item.objects.create(
                name=name,
                alias=alias or "",
                group=group or "",
                unit=unit or "",
                purchase_price=float(purchase_price or 0),
                mrp=float(mrp or 0),
                sale_discount=float(sale_discount or 0),
                purchase_discount=float(purchase_discount or 0),
                description=description or "",
                hsn_code=hsn_code or "NA",
                price=float(price or 0),
                gst_rate=float(gst_rate or 0),
                stock=int(stock or 0),
            )
            messages.success(request, f"🆕 New item '{name}' added successfully!")

        return redirect("view_items")

    return render(request, "items/add_item.html")


# 🟢 VIEW ALL ITEMS
@login_required(login_url='login_view')
def view_items(request):
    search = request.GET.get("search", "")
    items = Item.objects.all().order_by("id")
    if search:
        items = items.filter(name__icontains=search)
    return render(request, "items/view_items.html", {"items": items, "search": search})


# ✏️ EDIT ITEM
@login_required(login_url='login_view')
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        item.name = request.POST.get("name", item.name)
        item.alias = request.POST.get("alias", item.alias)
        item.group = request.POST.get("group", item.group)
        item.unit = request.POST.get("unit", item.unit)
        item.purchase_price = request.POST.get("purchase_price", item.purchase_price)
        item.mrp = request.POST.get("mrp", item.mrp)
        item.sale_discount = request.POST.get("sale_discount", item.sale_discount)
        item.purchase_discount = request.POST.get("purchase_discount", item.purchase_discount)
        item.description = request.POST.get("description", item.description)
        item.hsn_code = request.POST.get("hsn_code", item.hsn_code)
        item.price = request.POST.get("price", item.price)
        item.gst_rate = request.POST.get("gst_rate", item.gst_rate)
        item.stock = request.POST.get("stock", item.stock)
        item.save()

        messages.success(request, f"✅ Item '{item.name}' updated successfully!")
        return redirect("view_items")

    return render(request, "items/edit_item.html", {"item": item})


# 🗑️ DELETE ITEM
@login_required(login_url='login_view')
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.delete()
    messages.success(request, f"🗑️ Item '{item.name}' deleted successfully!")
    return redirect("view_items")


# 🧾 CREATE BILL
@login_required(login_url='login_view')
@transaction.atomic
def create_bill(request):
    items = Item.objects.all()
    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "Walk-in Customer")
        customer_phone = request.POST.get("customer_phone", "")
        customer_address = request.POST.get("customer_address", "")

        item_ids = request.POST.getlist("item_id[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        if not item_ids:
            messages.warning(request, "⚠️ Please select at least one product!")
            return redirect("create_bill")

        bill = Bill.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            date=timezone.now(),
            total_amount=0,
            gst_amount=0,
            net_amount=0,
        )

        total_amount = Decimal(0)
        total_gst = Decimal(0)

        for i, item_id in enumerate(item_ids):
            try:
                item = Item.objects.get(id=item_id)
                qty = int(quantities[i]) if quantities[i].isdigit() else 0
                price = Decimal(prices[i] or 0)
                gst_rate = Decimal(item.gst_rate or 0)
                taxable = price * qty
                gst_amount = (taxable * gst_rate) / 100
                line_total = taxable + gst_amount

                BillItem.objects.create(
                    bill=bill, item=item, quantity=qty,
                    price=price, gst_rate=gst_rate,
                    gst_amount=gst_amount, total=line_total
                )

                if item.stock >= qty:
                    item.stock -= qty
                    item.save()

                total_amount += taxable
                total_gst += gst_amount
            except Item.DoesNotExist:
                continue

        bill.total_amount = total_amount
        bill.gst_amount = total_gst
        bill.net_amount = total_amount + total_gst
        bill.save()

        messages.success(request, f"✅ Bill #{bill.id} created successfully!")
        return redirect("bill_detail", bill_id=bill.id)

    return render(request, "items/create_bill.html", {"items": items})


# 🧾 BILL DETAIL
@login_required(login_url='login_view')
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, "items/bill_detail.html", {
        "bill": bill,
        "bill_items": bill.items.all().order_by("id"),
    })


# 🧾 VIEW BILLS
@login_required(login_url='login_view')
def view_bills(request):
    search = request.GET.get('search', '').strip()
    bills = Bill.objects.filter(items__isnull=False).distinct().order_by("-date")

    if search:
        bills = bills.filter(
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(date__icontains=search)
        ).distinct()

    # ✅ Add Pagination (10 bills per page)
    paginator = Paginator(bills, 10)
    page = request.GET.get('page')

    try:
        bills = paginator.page(page)
    except PageNotAnInteger:
        bills = paginator.page(1)
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)

    # Calculate totals for visible bills only
    total_gst = sum(b.gst_amount for b in bills)
    total_amount = sum(b.total_amount for b in bills)
    grand_total = sum(b.net_amount for b in bills)

    return render(request, "items/view_bills.html", {
        "bills": bills,
        "search": search,
        "total_gst": total_gst,
        "total_amount": total_amount,
        "grand_total": grand_total,
        "paginator": paginator,
    })

# 💰 CREATE ESTIMATE
@login_required(login_url='login_view')
@transaction.atomic
def create_estimate(request):
    items = Item.objects.all()
    if request.method == "POST":
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        customer_address = request.POST.get("customer_address")

        estimate = EstimateBill.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            date=timezone.now(),
            total_amount=0,
            net_amount=0,
        )

        total_amount = 0
        item_ids = request.POST.getlist("item")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("price")

        for i in range(len(item_ids)):
            if not item_ids[i]:
                continue
            item = get_object_or_404(Item, id=item_ids[i])
            qty = float(quantities[i]) if quantities[i] else 1
            price = float(prices[i]) if prices[i] else item.price
            total = qty * price
            total_amount += total

            EstimateItem.objects.create(
                estimate=estimate, item=item,
                quantity=qty, price=price, total=total
            )

        estimate.total_amount = total_amount
        estimate.net_amount = total_amount
        estimate.save()

        messages.success(request, f"✅ Estimate #{estimate.id} created successfully!")
        return redirect("estimate_bill", bill_id=estimate.id)

    return render(request, "items/create_estimate.html", {"items": items})


# 🧾 ESTIMATE DETAIL
@login_required(login_url='login_view')
def estimate_bill(request, bill_id):
    estimate = get_object_or_404(EstimateBill, id=bill_id)
    return render(request, "items/estimate_bill.html", {
        "bill": estimate,
        "bill_items": estimate.items.all().order_by("id"),
    })


# 🧾 VIEW ALL ESTIMATES
@login_required(login_url='login_view')
def view_estimates(request):
    search = request.GET.get('search', '').strip()
    estimates = EstimateBill.objects.all().order_by('-date')

    if search:
        estimates = estimates.filter(
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search) |
            Q(items__item__name__icontains=search)
        ).distinct()

    # ✅ Add Pagination (10 estimates per page)
    paginator = Paginator(estimates, 10)
    page = request.GET.get('page')

    try:
        estimates = paginator.page(page)
    except PageNotAnInteger:
        estimates = paginator.page(1)
    except EmptyPage:
        estimates = paginator.page(paginator.num_pages)

    # 💰 Calculate totals (for current page)
    total_amount = sum(e.total_amount for e in estimates)
    grand_total = sum(e.net_amount for e in estimates)

    return render(request, "items/view_estimates.html", {
        "estimates": estimates,
        "search": search,
        "total_amount": total_amount,
        "grand_total": grand_total,
        "paginator": paginator,
    })


# 🖨️ PRINT ESTIMATE
@login_required(login_url='login_view')
def print_estimate(request, id):
    estimate = get_object_or_404(EstimateBill, id=id)
    return render(request, "items/estimate_print.html", {
        "bill": estimate,
        "bill_items": estimate.items.all(),
    })


# 🌍 PRODUCT AJAX
@login_required(login_url='login_view')
def get_product_details(request):
    product_id = request.GET.get('product_id')
    product = get_object_or_404(Item, id=product_id)
    return JsonResponse({
        'hsn_code': product.hsn_code,
        'price': product.price,
    })


# 📊 BASE CONTEXT
def base_context(request):
    return {'total_estimates': EstimateBill.objects.count()}


# 💼 CUSTOMER SUMMARY (Fixed & Working)
# 💼 CUSTOMER SUMMARY (With Payments Included)
@login_required(login_url='login_view')
# 💼 CUSTOMER SUMMARY (Merged by Name — Fix for Duplicate Customers)
@login_required(login_url='login_view')
def customer_summary(request):
    # Bills total
    bill_data = (
        Bill.objects.values('customer_name', 'customer_phone')
        .annotate(total_bills=Coalesce(Sum('net_amount'),
                V(0, output_field=DecimalField(max_digits=12, decimal_places=2))))
    )

    # Estimates total
    estimate_data = (
        EstimateBill.objects.values('customer_name', 'customer_phone')
        .annotate(total_estimates=Coalesce(Sum('net_amount'),
                V(0, output_field=DecimalField(max_digits=12, decimal_places=2))))
    )

    # Payments total
    payment_data = (
        CustomerPayment.objects.values('customer_name', 'customer_phone')
        .annotate(total_payments=Coalesce(Sum('amount'),
                V(0, output_field=DecimalField(max_digits=12, decimal_places=2))))
    )

    combined = {}

    # Merge bills
    for b in bill_data:
        key = b['customer_name'].strip().lower()
        combined[key] = {
            'customer_name': b['customer_name'],
            'customer_phone': b['customer_phone'] or '',
            'total_bills': b['total_bills'],
            'total_estimates': 0,
            'total_payments': 0,
            'total_udhar': b['total_bills'],
        }

    # Merge estimates
    for e in estimate_data:
        key = e['customer_name'].strip().lower()
        if key in combined:
            combined[key]['total_estimates'] += e['total_estimates']
            combined[key]['total_udhar'] += e['total_estimates']
            if not combined[key]['customer_phone']:
                combined[key]['customer_phone'] = e['customer_phone'] or ''
        else:
            combined[key] = {
                'customer_name': e['customer_name'],
                'customer_phone': e['customer_phone'] or '',
                'total_bills': 0,
                'total_estimates': e['total_estimates'],
                'total_payments': 0,
                'total_udhar': e['total_estimates'],
            }

    # Merge payments
    for p in payment_data:
        key = p['customer_name'].strip().lower()
        if key in combined:
            combined[key]['total_payments'] += p['total_payments']
            if not combined[key]['customer_phone']:
                combined[key]['customer_phone'] = p['customer_phone'] or ''
        else:
            combined[key] = {
                'customer_name': p['customer_name'],
                'customer_phone': p['customer_phone'] or '',
                'total_bills': 0,
                'total_estimates': 0,
                'total_payments': p['total_payments'],
                'total_udhar': 0,
            }

    # Calculate remaining balance safely
    for value in combined.values():
        remaining = value['total_udhar'] - value['total_payments']
        value['remaining_balance'] = remaining if remaining > 0 else 0

    customers = sorted(combined.values(), key=lambda x: x['customer_name'])
    return render(request, "items/customer_summary.html", {"customers": customers})


# 💵 ADD PAYMENT VIEW (with corrected remaining balance)
@login_required(login_url='login_view')
def add_payment(request, name):
    """
    Records a new payment for the given customer (by name).
    Updates CustomerPayment and redirects to the ledger.
    """
    bill = Bill.objects.filter(customer_name=name).first()
    estimate = EstimateBill.objects.filter(customer_name=name).first()

    if not bill and not estimate:
        messages.error(request, "⚠️ Customer not found!")
        return redirect("customer_summary")

    customer_name = name
    customer_phone = bill.customer_phone if bill else (estimate.customer_phone if estimate else "")

    # Calculate outstanding balance
    total_bills = (
        Bill.objects.filter(customer_name=customer_name)
        .aggregate(total=Sum("net_amount"))["total"] or 0
    )
    total_estimates = (
        EstimateBill.objects.filter(customer_name=customer_name)
        .aggregate(total=Sum("net_amount"))["total"] or 0
    )
    total_payments = (
        CustomerPayment.objects.filter(customer_name=customer_name)
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    remaining_balance = (total_bills + total_estimates) - total_payments
    if remaining_balance < 0:
        remaining_balance = 0  # Prevent showing negative values

    # Handle POST
    if request.method == "POST":
        amount = request.POST.get("amount")
        note = request.POST.get("note", "")

        try:
            amount = Decimal(amount)
        except (InvalidOperation, TypeError):
            messages.error(request, "⚠️ Invalid amount entered.")
            return redirect("add_payment", name=customer_name)

        if amount <= 0:
            messages.warning(request, "⚠️ Amount must be greater than zero.")
            return redirect("add_payment", name=customer_name)

        CustomerPayment.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            amount=amount,
            date=timezone.now(),
            note=note,
        )

        messages.success(request, f"✅ Payment of ₹{amount} recorded for {customer_name}.")
        return redirect("customer_detail", name=customer_name)

    context = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "remaining_balance": remaining_balance,
    }
    return render(request, "items/add_payment.html", context)




# 💰 CUSTOMER DETAIL / LEDGER (with payment tracking)
@login_required(login_url='login_view')
def customer_detail(request, name):
    # Get all bills, estimates, and payments for this customer
    bills = Bill.objects.filter(customer_name=name).order_by("-date")
    estimates = EstimateBill.objects.filter(customer_name=name).order_by("-date")
    payments = CustomerPayment.objects.filter(customer_name=name).order_by("-date")

    # Calculate totals
    total_bill = bills.aggregate(Sum("net_amount"))["net_amount__sum"] or 0
    total_estimate = estimates.aggregate(Sum("net_amount"))["net_amount__sum"] or 0
    total_payment = payments.aggregate(Sum("amount"))["amount__sum"] or 0

    total_udhar = total_bill + total_estimate
    remaining_balance = total_udhar - total_payment

    context = {
        "customer_name": name,
        "bills": bills,
        "estimates": estimates,
        "payments": payments,
        "total_bill": total_bill,
        "total_estimate": total_estimate,
        "total_payment": total_payment,
        "total_udhar": total_udhar,
        "remaining_balance": remaining_balance,
    }

    return render(request, "items/customer_detail.html", context)

# 💰 CUSTOMER DETAIL / LEDGER (with payment tracking)
@login_required(login_url='login_view')
def customer_detail(request, name):
    # Get all bills, estimates, and payments for this customer
    bills = Bill.objects.filter(customer_name=name).order_by("-date")
    estimates = EstimateBill.objects.filter(customer_name=name).order_by("-date")
    payments = CustomerPayment.objects.filter(customer_name=name).order_by("-date")

    # Calculate totals
    total_bill = bills.aggregate(Sum("net_amount"))["net_amount__sum"] or 0
    total_estimate = estimates.aggregate(Sum("net_amount"))["net_amount__sum"] or 0
    total_payment = payments.aggregate(Sum("amount"))["amount__sum"] or 0

    total_udhar = total_bill + total_estimate
    remaining_balance = total_udhar - total_payment

    context = {
        "customer_name": name,
        "bills": bills,
        "estimates": estimates,
        "payments": payments,
        "total_bill": total_bill,
        "total_estimate": total_estimate,
        "total_payment": total_payment,
        "total_udhar": total_udhar,
        "remaining_balance": remaining_balance,
    }

    return render(request, "items/customer_detail.html", context)


# 💵 ADD PAYMENT VIEW (based on customer name)
@login_required(login_url='login_view')
def add_payment(request, name):
    """
    Records a new payment for the given customer (by name).
    Updates CustomerPayment and redirects to the ledger.
    """
    # Fetch related customer data from bills or estimates
    bill = Bill.objects.filter(customer_name=name).first()
    estimate = EstimateBill.objects.filter(customer_name=name).first()

    if not bill and not estimate:
        messages.error(request, "⚠️ Customer not found!")
        return redirect("customer_summary")

    customer_name = name
    customer_phone = bill.customer_phone if bill else (estimate.customer_phone if estimate else "")

    # Calculate outstanding balance
    total_bills = (
        Bill.objects.filter(customer_name=customer_name)
        .aggregate(total=Sum("net_amount"))["total"] or 0
    )
    total_estimates = (
        EstimateBill.objects.filter(customer_name=customer_name)
        .aggregate(total=Sum("net_amount"))["total"] or 0
    )
    total_payments = (
        CustomerPayment.objects.filter(customer_name=customer_name)
        .aggregate(total=Sum("amount"))["total"] or 0
    )
    remaining_balance = (total_bills + total_estimates) - total_payments

    # Handle POST
    if request.method == "POST":
        amount = request.POST.get("amount")
        note = request.POST.get("note", "")

        try:
            amount = Decimal(amount)
        except (InvalidOperation, TypeError):
            messages.error(request, "⚠️ Invalid amount entered.")
            return redirect("add_payment", name=customer_name)

        if amount <= 0:
            messages.warning(request, "⚠️ Amount must be greater than zero.")
            return redirect("add_payment", name=customer_name)

        # Save payment record
        CustomerPayment.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            amount=amount,
            date=timezone.now(),
            note=note,
        )

        messages.success(request, f"✅ Payment of ₹{amount} recorded for {customer_name}.")
        return redirect("customer_detail", name=customer_name)

    context = {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "remaining_balance": remaining_balance,
    }
    return render(request, "items/add_payment.html", context)

@login_required(login_url='login_view')
def delete_customer(request, name):
    """
    Deletes all bills, estimates, and payments for the given customer.
    """
    if request.method == "POST":
        # Delete all records related to this customer
        Bill.objects.filter(customer_name=name).delete()
        EstimateBill.objects.filter(customer_name=name).delete()
        CustomerPayment.objects.filter(customer_name=name).delete()

        messages.success(request, f"🗑️ All records for customer '{name}' have been deleted successfully.")
        return redirect("customer_summary")

    messages.error(request, "⚠️ Invalid request.")
    return redirect("customer_summary")
