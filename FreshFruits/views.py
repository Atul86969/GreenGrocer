from django.shortcuts import render,redirect
from django.http import HttpResponse
from math import ceil
import json
from datetime import datetime
import razorpay
from django.core.mail import send_mail
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import Product,Contact,Orders,OrderUpdate
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,DjangoUnicodeDecodeError,force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator


def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    context= {'allProds':allProds}

    return render(request,"index.html",context)


def about(request):
    return render(request,'about.html')


def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")


def header(request):
    return render(request,'header.html')
    


def register(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('uname')
        pwd = request.POST.get('upass')
        cpwd = request.POST.get('ucon')
        if name == '' or pwd == '' or cpwd == '':
            context['errmsg'] = 'Fields cannot be empty'
            return render(request, 'register.html', context)
        elif pwd != cpwd:
            context['notmatch'] = 'Password did not match'
            return render(request, 'register.html', context)
        else:

            u = User.objects.create(username=name,email=name)
            u.set_password(pwd)
            u.save()
            context['success']='Registration Successfull'
            return render(request, 'register.html', context)

    else:   
        
        return render(request, 'register.html')


def user_login(request):
    context={}
    if request.method=="POST":
        user_name = request.POST['uname']
        upassword = request.POST['upass']
        if user_name == '' or upassword == '' :
            context['errmsg'] = 'Fields cannot be empty'
            return render(request,"login.html",context)
        else:
            u=authenticate(username=user_name,password=upassword)
            if u is not None:
                login(request,u)
                # print(request.user.is_authenticated)
                return redirect("/")
            return render(request,'login.html')
    else:
        return render(request,'login.html')


def  user_logout(request):
    logout(request)
    return redirect('/user_login')



def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/user_login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank = True
# # PAYMENT INTEGRATION

        id = Order.order_id
        oid=str(id)+"GreenGrocer"
        
        Order.oid = oid
        Order.save()
        
        
        client = razorpay.Client(auth=('rzp_test_R7kWkFU6ZllnWF', 'W0gE85soRmV6WanAQr1nW69n'))
        payment_data = {
            'amount': int(Order.amount) * 100,  # Amount in paise
            'currency': 'INR',  # Currency code (INR for Indian Rupee)
            'receipt': f'order_{Order.oid}',
            'payment_capture': 1,  # Auto-capture payment
            # Add additional parameters as needed
        }

        payment = client.order.create(data=payment_data)

        return render(request, 'razorpay.html', {'order': Order, 'payment': payment})

    return render(request, 'checkout.html')


def payment_status(request):
    print(request.GET)

    payment_id = request.GET.get('payment_id')
    
    is_success = True
    context = {
        'payment_id': payment_id,
        'is_success': is_success,
    }
    return render(request, 'payment_status.html', context)










