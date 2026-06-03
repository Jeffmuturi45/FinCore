from django.conf import settings

def sacco_context(request):
    return {
        "SACCO_NAME": getattr(settings, "SACCO_NAME", "SACCO"),
        "SACCO_CURRENCY": getattr(settings, "SACCO_CURRENCY", "KES"),
        "SACCO_CURRENCY_SYMBOL": getattr(settings, "SACCO_CURRENCY_SYMBOL", "KSh"),
    }