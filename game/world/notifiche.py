"""
Notifiche email allo staff (Fase K, pre-release, punto 2 della checklist
dell'utente): al momento solo la notifica di nuova registrazione
account, inviata a STAFF_NOTIFICATION_EMAIL tramite il relay SMTP Brevo
gia' configurato in server/conf/settings.py / secret_settings.py.

Fallisce in modo silenzioso (solo un log server) se le credenziali non
sono ancora state inserite o se l'invio fallisce per qualsiasi motivo:
un problema di posta non deve MAI impedire la creazione di un account.
"""

from django.conf import settings

from evennia.utils import logger


def notifica_nuovo_account(username, indirizzo_ip):
    if not getattr(settings, "NOTIFY_STAFF_ON_NEW_ACCOUNT", False):
        return
    if not getattr(settings, "EMAIL_HOST_PASSWORD", ""):
        logger.log_info(
            "Notifica nuovo account saltata (EMAIL_HOST_PASSWORD non configurato in "
            "secret_settings.py)."
        )
        return

    destinatario = getattr(settings, "STAFF_NOTIFICATION_EMAIL", None)
    if not destinatario:
        return

    try:
        from django.core.mail import send_mail

        send_mail(
            subject=f"[CthulhuMud] Nuova registrazione: {username}",
            message=(
                f"E' stato appena creato un nuovo account su CthulhuMud.\n\n"
                f"Nome utente: {username}\n"
                f"Indirizzo IP: {indirizzo_ip}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            fail_silently=False,
        )
    except Exception:
        logger.log_trace("Invio della notifica email di nuova registrazione fallito.")
