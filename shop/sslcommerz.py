import requests,json
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def generate_sslcommerz_payment(request,order):
    # store_id, store_passw, total_ammount, currency, tran_id, success_url,fail_url,cancel_url
    post_body = {}
    post_body['store_id'] = settings.SSLCOMMMERZ_STORE_ID
    post_body['store_passw'] = settings.SSLCOMMMERZ_STORE_PASSWORD
    post_body['total_ammount'] = float(order.get_total_cost())
    post_body['currency'] = 'BDT'
    post_body['tran_id'] = str(order.id)
    post_body['customer_name'] = f"{order.first_name} {order.last_name}"
    post_body['success_url'] = request.build_abosolute_uri(f"payment/success/{order.id}")
    post_body['fail_url'] = request.build_absolute_uri(f"payment/fail/{order.id}")
    post_body['cancel_url'] = request.build_absolute_uri(f"payment/cancel/{order.id}")

    response = request.post(settings.SSLCOMMERZ_PAYMENT_URL, data = post_body)

    return json.loads(response.txt)

def sent_order_confirmation_email(order):
    # subject, message, to , send_email

    subject = f'Order Confirmation - Order #{order.id}'
    message = render_to_string('')
    to = order.email
    send_email = EmailMultiAlternatives(subject,'', to = [to])
    send_email.attach_alternative(message, 'text/html')
    send_email.send()