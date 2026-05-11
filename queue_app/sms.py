import logging
import os

logger = logging.getLogger('queue_app')


def send_called_notification(entry):
    """Send SMS to customer when their turn is called."""
    from twilio.rest import Client

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token  = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number]):
        logger.warning("Twilio credentials not configured — SMS not sent for turn %s", entry.turn_number)
        return None

    client = Client(account_sid, auth_token)
    body = (
        f"Hola {entry.name}, ¡es tu turno! "
        f"Tu número es el {entry.turn_number}. "
        f"Por favor acércate a la ventanilla."
    )
    message = client.messages.create(
        to=entry.phone,
        from_=from_number,
        body=body,
    )
    logger.info("SMS sent to turn %s (SID: %s)", entry.turn_number, message.sid)
    return message.sid
