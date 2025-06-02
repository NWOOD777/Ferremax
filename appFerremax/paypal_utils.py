import paypalrestsdk
from django.conf import settings

# Configurar SDK de PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" o "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

def crear_pago(items, total, descripcion, redirect_urls):
    """
    Crea un pago en PayPal
    
    Args:
        items: Lista de productos a comprar
        total: Monto total del pago
        descripcion: Descripción del pago
        redirect_urls: URLs de redirección tras el pago
    
    Returns:
        El objeto de pago creado en PayPal o None si falló
    """
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": redirect_urls,
        "transactions": [{
            "item_list": {
                "items": items
            },
            "amount": {
                "total": str(total),
                "currency": "USD"
            },
            "description": descripcion
        }]
    })

    if payment.create():
        return payment
    else:
        print(payment.error)
        return None

def ejecutar_pago(payment_id, payer_id):
    """
    Ejecuta un pago aprobado en PayPal
    
    Args:
        payment_id: ID del pago en PayPal
        payer_id: ID del pagador en PayPal
    
    Returns:
        True si el pago se ejecutó correctamente, False en caso contrario
    """
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return True
    else:
        print(payment.error)
        return False