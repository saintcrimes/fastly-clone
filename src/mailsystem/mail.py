from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from ..mailsystem.config import Config

# fm_schemas.validate_path = lambda path: True

BASE_DIR = Path(
    __file__
).resolve().parent.parent

mail_config = ConnectionConfig(
    MAIL_USERNAME= Config.MAIL_USERNAME,
    MAIL_PASSWORD = Config.MAIL_PASSWORD,
    MAIL_FROM = Config.MAIL_FROM,
    MAIL_PORT = Config.MAIL_PORT,
    MAIL_SERVER = Config.MAIL_SERVER,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER= Path(BASE_DIR, 'templates/mail')
)


mail = FastMail(
    config=mail_config
)

def create_message(recipients: list[str], subject: str, body:str = None, template_body: dict = None):
    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        template_body=template_body,
        subtype=MessageType.html,
        # attachments=attachments
    )
    '''
    if you want to send files through the email, 
    you can uncomment the attachments.
    
    '''
    return message
