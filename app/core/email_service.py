import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None

    async def send_otp_email(self, to_email: str, otp: str):
        if not self.client or not self.from_email:
            print("Email service not configured. OTP:", otp)
            return False

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='Your SkillSync Verification Code',
            html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                    <h2 style="color: #4F46E5; text-align: center;">Welcome to SkillSync</h2>
                    <p style="font-size: 16px; color: #374151;">Use the following verification code to complete your registration:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; padding: 10px 20px; background-color: #F3F4F6; border-radius: 5px; letter-spacing: 5px;">{otp}</span>
                    </div>
                    <p style="font-size: 14px; color: #6B7280; text-align: center;">This code will expire in 10 minutes.</p>
                </div>
            '''
        )
        try:
            import anyio
            response = await anyio.to_thread.run_sync(self.client.send, message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

email_service = EmailService()
