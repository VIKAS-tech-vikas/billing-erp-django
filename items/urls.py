from django.urls import path
from . import views

urlpatterns = [

    # 📦 Item Management
    path('add-item/', views.add_item, name='add_item'),
    path('view-items/', views.view_items, name='view_items'),
    path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),

    # 🧾 Billing System
    path('create-bill/', views.create_bill, name='create_bill'),
    path('view-bills/', views.view_bills, name='view_bills'),
    path('bill/<int:bill_id>/', views.bill_detail, name='bill_detail'),

    # 💰 Estimate System (Without GST)
    path('create-estimate/', views.create_estimate, name='create_estimate'),
    path('estimate/<int:bill_id>/', views.estimate_bill, name='estimate_bill'),

    # 🧾 AJAX for Product Details (HSN + Price)
    path('get-product-details/', views.get_product_details, name='get_product_details'),

    # 📋 View & Print Estimates
    path('view-estimates/', views.view_estimates, name='view_estimates'),
    path('print-estimate/<int:id>/', views.print_estimate, name='print_estimate'),

    # 👤 Authentication
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),

    # 👥 Customer Management
    path('customer-summary/', views.customer_summary, name='customer_summary'),
    path('customer/<str:name>/', views.customer_detail, name='customer_detail'),
    path('add-payment/<str:name>/', views.add_payment, name='add_payment'),
    path('delete-customer/<str:name>/', views.delete_customer, name='delete_customer'),


]
