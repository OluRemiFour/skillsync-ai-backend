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
            print(f"Error sending OTP email: {e}")
            return False

    async def send_password_reset_email(self, to_email: str, token: str):
        if not self.client or not self.from_email:
            print("Email service not configured. Reset Token:", token)
            return False

        reset_link = f"http://localhost:5173/reset-password?token={token}"
        
        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='Reset Your SkillSync Password',
            html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                    <h2 style="color: #4F46E5; text-align: center;">Password Reset Request</h2>
                    <p style="font-size: 16px; color: #374151;">We received a request to reset your password. Click the button below to proceed:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #000000; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
                    </div>
                    <p style="font-size: 14px; color: #6B7280;">If you didn't request this, you can safely ignore this email.</p>
                </div>
            '''
        )
        try:
            import anyio
            response = await anyio.to_thread.run_sync(self.client.send, message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending reset email: {e}")
            return False

    async def send_general_email(self, to_email: str, subject: str, student_name: str, content: str):
        if not self.client or not self.from_email:
            print(f"Email service not configured. Message to {to_email}: {content}")
            return True # Pretend success for dev

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject=subject,
            html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">Message from SkillSync Recruiter</h2>
                    <p style="font-size: 16px; color: #374151;">Hello {student_name},</p>
                    <div style="background-color: #F3F4F6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="font-size: 16px; color: #111827; white-space: pre-line;">{content}</p>
                    </div>
                    <p style="font-size: 14px; color: #6B7280;">Log in to your dashboard to reply.</p>
                </div>
            '''
        )
        try:
            import anyio
            response = await anyio.to_thread.run_sync(self.client.send, message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending general email: {e}")
            return False

    async def send_interview_email(self, to_email: str, student_name: str, date: str, time: str, invite_type: str, notes: str):
        if not self.client or not self.from_email:
            print(f"Email service not configured. Interview for {to_email} on {date}")
            return True

        message = Mail(
            from_email=self.from_email,
            to_emails=to_email,
            subject='SkillSync Interview Invitation',
            html_content=f'''
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
                    <h2 style="color: #4F46E5; text-align: center;">Interview Invitation</h2>
                    <p style="font-size: 16px; color: #374151;">Hello {student_name},</p>
                    <p style="font-size: 16px; color: #374151;">You have been invited for an interview!</p>
                    <div style="background-color: #F3F4F6; padding: 20px; border-radius: 5px; margin: 20px 0;">
                        <p><strong>Date:</strong> {date}</p>
                        <p><strong>Time:</strong> {time}</p>
                        <p><strong>Type:</strong> {invite_type}</p>
                        {f"<p><strong>Notes:</strong> {notes}</p>" if notes else ""}
                    </div>
                    <p style="font-size: 14px; color: #6B7280; text-align: center;">Please confirm your availability by replying to this email or via the dashboard.</p>
                </div>
            '''
        )
        try:
            import anyio
            response = await anyio.to_thread.run_sync(self.client.send, message)
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending interview email: {e}")
            return False

email_service = EmailService()
