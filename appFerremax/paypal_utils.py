import paypalrestsdk
from django.conf import settings

# Configurar SDK de PayPal con valores predeterminados para desarrollo
paypalrestsdk.configure({
    "mode": getattr(settings, 'PAYPAL_MODE', 'sandbox'),  # "sandbox" o "live"
    "client_id": getattr(settings, 'PAYPAL_CLIENT_ID', 'your-client-id'),
    "client_secret": getattr(settings, 'PAYPAL_CLIENT_SECRET', 'your-client-secret')
})

def crear_pago(total, descripcion, return_url):
    """
    Crea un pago en PayPal
    
    Args:
        total: Monto total del pago
        descripcion: Descripción del pago
        return_url: URL de redirección tras el pago
    
    Returns:
        (url_aprobacion, payment_id): URL para aprobar el pago y ID del pago
        o (None, None) si falló
    """
    try:
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": return_url
            },
            "transactions": [{
                "amount": {
                    "total": str(total),
                    "currency": "USD"
                },
                "description": descripcion
            }]
        })
        
        # Crear el pago
        if payment.create():
            # Extraer la URL de aprobación
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return approval_url, payment.id
        else:
            print(f"Error al crear el pago: {payment.error}")
            return None, None
    except Exception as e:
        print(f"Error en PayPal: {str(e)}")
        return None, None

def ejecutar_pago(payment_id, payer_id):
    """
    Ejecuta un pago aprobado en PayPal
    
    Args:
        payment_id: ID del pago en PayPal
        payer_id: ID del pagador en PayPal
    
    Returns:
        (bool, dict): (True, detalles_pago) si el pago se ejecutó correctamente, (False, {}) en caso contrario
    """
    try:
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Extraer detalles del pago
            payment_details = {
                'payment_id': payment.id,
                'state': payment.state,
                'amount': payment.transactions[0].amount.total,
                'currency': payment.transactions[0].amount.currency
            }
            return True, payment_details
        else:
            print(f"Error al ejecutar el pago: {payment.error}")
            return False, {}
    except Exception as e:
        print(f"Error en PayPal: {str(e)}")
        return False, {}