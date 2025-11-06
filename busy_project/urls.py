from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# 🏠 Redirect root ('/') to Add Item page
def home_redirect(request):
    return redirect('add_item')

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Default route → redirect to Add Item
    path('', home_redirect, name='home'),

    # ✅ Include all URLs from items app
    path('', include('items.urls')),
]
