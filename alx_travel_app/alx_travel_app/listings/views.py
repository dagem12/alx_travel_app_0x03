from django.shortcuts import render

# Create your views here.
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Payment
import uuid
import json

@csrf_exempt
def initiate_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        booking_reference = str(uuid.uuid4())
        amount = data.get('amount')
        email = data.get('email')
        first_name = data.get('first_name', 'Guest')
        last_name = data.get('last_name', '')

        payment = Payment.objects.create(
            booking_reference=booking_reference,
            amount=amount
        )

        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }
        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": booking_reference,
            "callback_url": f"http://yourdomain.com/api/verify-payment/{booking_reference}/",
            "return_url": f"http://yourdomain.com/payment-success/{booking_reference}/",
            "customization[title]": "Travel Booking Payment"
        }

        response = requests.post(chapa_url, json=payload, headers=headers)
        res_data = response.json()

        if res_data.get('status') == 'success':
            payment.transaction_id = res_data['data']['tx_ref']
            payment.save()
            return JsonResponse({"checkout_url": res_data['data']['checkout_url']})
        else:
            return JsonResponse({"error": "Payment initiation failed"}, status=400)

@csrf_exempt
def verify_payment(request, booking_reference):
    try:
        payment = Payment.objects.get(booking_reference=booking_reference)
    except Payment.DoesNotExist:
        return JsonResponse({"error": "Invalid reference"}, status=404)

    url = f"https://api.chapa.co/v1/transaction/verify/{payment.booking_reference}"
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data['status'] == 'success' and res_data['data']['status'] == 'success':
        payment.status = 'Completed'
        payment.save()
        # TODO: Send confirmation email with Celery
        return JsonResponse({"message": "Payment successful"})
    else:
        payment.status = 'Failed'
        payment.save()
        return JsonResponse({"message": "Payment failed"}, status=400)