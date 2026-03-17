import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

logger = logging.getLogger(__name__)

def _get_email_subject() -> str:
    return "Votre code de vérification Karangou Studios"

def _get_email_html_template(otp_code: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Code Karangou Studios</title>
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:'Segoe UI',Arial,sans-serif; background:#1a1a1a; color:#fff; }}
            .container {{ max-width:600px; margin:30px auto; background:#222; border-radius:16px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.3); }}
            .header {{ background:linear-gradient(135deg, #ff6b35, #ff8c5a); padding:40px 30px; text-align:center; color:white; }}
            .header h1 {{ font-size:32px; font-weight:700; margin:0; letter-spacing:1px; }}
            .header p {{ margin:10px 0 0; font-size:17px; opacity:0.95; }}
            .content {{ padding:50px 40px; text-align:center; }}
            .otp {{ 
                display:inline-block; 
                background:#2a2a2a; 
                color:#ff6b35; 
                font-size:52px; 
                font-weight:800; 
                letter-spacing:14px; 
                padding:25px 50px; 
                border:3px solid #ff6b35; 
                border-radius:16px; 
                margin:30px 0; 
                font-family:'Courier New', monospace;
            }}
            .text {{ color:#aaa; font-size:17px; line-height:1.7; margin:25px 0; }}
            .highlight {{ color:#ff6b35; font-weight:600; }}
            .footer {{ background:#1a1a1a; padding:30px; text-align:center; font-size:13px; color:#777; }}
            .footer a {{ color:#ff6b35; text-decoration:none; }}
            @media (max-width:600px) {{
                .container {{ border-radius:0; margin:0; }}
                .header, .content {{ padding-left:20px; padding-right:20px; }}
                .otp {{ font-size:40px; letter-spacing:8px; padding:20px 30px; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 KARANGOU STUDIOS</h1>
                <p>Vérification de votre compte</p>
            </div>
            <div class="content">
                <h2 style="color:#fff; margin-bottom:25px; font-size:26px; font-weight:normal;">
                    Voici votre code de sécurité
                </h2>
                <div class="otp">{otp_code}</div>
                <p class="text">
                    Ce code est valable pendant <span class="highlight">15 minutes</span>.<br>
                    Si vous n'avez pas demandé cette vérification, ignorez cet email.
                </p>
            </div>
            <div class="footer">
                <p>© {timezone.now().year} <strong>Karangou Studios</strong> • Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """

def _get_email_text_template(otp_code: str) -> str:
    return f"""
Votre code de vérification Karangou Studios : {otp_code}

Ce code expire dans 15 minutes.
Ne partagez jamais ce code.

© {timezone.now().year} Karangou Studios - Tous droits réservés
    """.strip()

def send_otp_email(recipient_email: str, otp_code: str) -> bool:
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@karangou.com')
        msg = EmailMultiAlternatives(
            subject=_get_email_subject(),
            body=_get_email_text_template(otp_code),
            from_email=from_email,
            to=[recipient_email],
        )
        msg.attach_alternative(_get_email_html_template(otp_code), "text/html")
        msg.send()
        logger.info(f"Email OTP envoyé à {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Échec envoi email OTP : {e}")
        return False
