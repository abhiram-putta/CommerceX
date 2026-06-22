"""
Email service for sending notifications and transactional emails.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EmailService:
    """Service for sending emails."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content
            text_content: Plain text content (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add text part
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_order_confirmation(
        self,
        to_email: str,
        customer_name: str,
        order_id: UUID,
        order_number: str,
        order_date: datetime,
        items: List[dict],
        subtotal: float,
        tax: float,
        shipping: float,
        total: float,
        shipping_address: dict,
    ) -> bool:
        """
        Send order confirmation email.

        Args:
            to_email: Customer email
            customer_name: Customer name
            order_id: Order UUID
            order_number: Order number
            order_date: Order date
            items: List of order items
            subtotal: Subtotal amount
            tax: Tax amount
            shipping: Shipping amount
            total: Total amount
            shipping_address: Shipping address dict

        Returns:
            True if sent successfully
        """
        subject = f"Order Confirmation - #{order_number}"

        # Build items HTML
        items_html = ""
        for item in items:
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>{item['product_name']}</strong><br>
                    <small>SKU: {item.get('sku', 'N/A')}</small>
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                    {item['quantity']}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    ₹{item['unit_price']:.2f}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    <strong>₹{item['total_price']:.2f}</strong>
                </td>
            </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0;">Order Confirmed!</h1>
            </div>

            <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p>Hi {customer_name},</p>
                <p>Thank you for your order! We're excited to let you know that we've received your order and it's being processed.</p>

                <div style="background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; border: 1px solid #ddd;">
                    <h2 style="margin-top: 0; color: #4CAF50;">Order Details</h2>
                    <p><strong>Order Number:</strong> #{order_number}</p>
                    <p><strong>Order Date:</strong> {order_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>

                <h3 style="margin-top: 30px;">Order Items</h3>
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f5f5f5;">
                            <th style="padding: 10px; text-align: left; border-bottom: 2px solid #ddd;">Item</th>
                            <th style="padding: 10px; text-align: center; border-bottom: 2px solid #ddd;">Qty</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Price</th>
                            <th style="padding: 10px; text-align: right; border-bottom: 2px solid #ddd;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <div style="text-align: right; margin-bottom: 20px;">
                    <p style="margin: 5px 0;">Subtotal: <strong>₹{subtotal:.2f}</strong></p>
                    <p style="margin: 5px 0;">Tax: <strong>₹{tax:.2f}</strong></p>
                    <p style="margin: 5px 0;">Shipping: <strong>₹{shipping:.2f}</strong></p>
                    <hr style="border: none; border-top: 2px solid #4CAF50; margin: 10px 0;">
                    <p style="margin: 5px 0; font-size: 1.2em;">Total: <strong style="color: #4CAF50;">₹{total:.2f}</strong></p>
                </div>

                <h3>Shipping Address</h3>
                <div style="background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">
                    <p style="margin: 5px 0;"><strong>{shipping_address.get('name', customer_name)}</strong></p>
                    <p style="margin: 5px 0;">{shipping_address.get('address_line1', '')}</p>
                    {f"<p style='margin: 5px 0;'>{shipping_address.get('address_line2', '')}</p>" if shipping_address.get('address_line2') else ''}
                    <p style="margin: 5px 0;">{shipping_address.get('city', '')}, {shipping_address.get('state', '')} {shipping_address.get('pincode', '')}</p>
                    <p style="margin: 5px 0;">{shipping_address.get('country', 'India')}</p>
                    <p style="margin: 5px 0;">Phone: {shipping_address.get('phone', '')}</p>
                </div>

                <div style="margin-top: 30px; padding: 15px; background-color: #e8f5e9; border-radius: 5px; border-left: 4px solid #4CAF50;">
                    <p style="margin: 0;"><strong>What's next?</strong></p>
                    <p style="margin: 10px 0 0 0;">We'll send you a shipping confirmation email with tracking details as soon as your order ships.</p>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="{settings.FRONTEND_URL}/orders/{order_id}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Track Your Order</a>
                </div>

                <p style="margin-top: 30px; font-size: 0.9em; color: #666;">
                    If you have any questions, please contact our customer support.
                </p>

                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">

                <p style="font-size: 0.85em; color: #999; text-align: center;">
                    © {datetime.now().year} {settings.APP_NAME}. All rights reserved.<br>
                    This email was sent to {to_email}
                </p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_order_shipped(
        self,
        to_email: str,
        customer_name: str,
        order_number: str,
        tracking_number: Optional[str] = None,
        carrier: Optional[str] = None,
        estimated_delivery: Optional[datetime] = None,
    ) -> bool:
        """Send order shipped notification."""
        subject = f"Your Order #{order_number} Has Shipped!"

        tracking_html = ""
        if tracking_number and carrier:
            tracking_html = f"""
            <div style="background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; border: 1px solid #ddd;">
                <p><strong>Carrier:</strong> {carrier}</p>
                <p><strong>Tracking Number:</strong> {tracking_number}</p>
                {f"<p><strong>Estimated Delivery:</strong> {estimated_delivery.strftime('%B %d, %Y')}</p>" if estimated_delivery else ""}
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #2196F3; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0;">📦 Your Order Has Shipped!</h1>
            </div>

            <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p>Hi {customer_name},</p>
                <p>Great news! Your order #{order_number} has been shipped and is on its way to you.</p>

                {tracking_html}

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/track/{tracking_number if tracking_number else order_number}"
                       style="background-color: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Track Shipment
                    </a>
                </div>

                <p>Thank you for shopping with us!</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_order_delivered(
        self,
        to_email: str,
        customer_name: str,
        order_number: str,
    ) -> bool:
        """Send order delivered notification."""
        subject = f"Order #{order_number} Delivered"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0;">✅ Order Delivered!</h1>
            </div>

            <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p>Hi {customer_name},</p>
                <p>Your order #{order_number} has been delivered. We hope you love your purchase!</p>

                <div style="background-color: #e8f5e9; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #4CAF50;">
                    <p style="margin: 0;"><strong>How was your experience?</strong></p>
                    <p style="margin: 10px 0 0 0;">We'd love to hear your feedback!</p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/review/{order_number}"
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Write a Review
                    </a>
                </div>

                <p>Thank you for choosing {settings.APP_NAME}!</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_password_reset(
        self,
        to_email: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email."""
        subject = "Reset Your Password"
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #FF9800; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0;">Password Reset Request</h1>
            </div>

            <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p>We received a request to reset your password.</p>
                <p>Click the button below to reset your password:</p>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}"
                       style="background-color: #FF9800; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>

                <p style="font-size: 0.9em; color: #666;">
                    If you didn't request this, please ignore this email. The link will expire in 24 hours.
                </p>

                <p style="font-size: 0.85em; color: #999; margin-top: 30px;">
                    Or copy and paste this link:<br>
                    <a href="{reset_link}" style="color: #FF9800; word-break: break-all;">{reset_link}</a>
                </p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)

    async def send_welcome_email(
        self,
        to_email: str,
        customer_name: str,
    ) -> bool:
        """Send welcome email to new users."""
        subject = f"Welcome to {settings.APP_NAME}!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #673AB7; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0;">
                <h1 style="margin: 0;">Welcome to {settings.APP_NAME}!</h1>
            </div>

            <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                <p>Hi {customer_name},</p>
                <p>Welcome aboard! We're thrilled to have you as part of our community.</p>

                <div style="background-color: white; padding: 15px; margin: 20px 0; border-radius: 5px; border: 1px solid #ddd;">
                    <h3 style="margin-top: 0; color: #673AB7;">Get Started</h3>
                    <ul style="padding-left: 20px;">
                        <li>Browse our wide selection of products</li>
                        <li>Add items to your wishlist</li>
                        <li>Enjoy fast and secure checkout</li>
                        <li>Track your orders in real-time</li>
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/products"
                       style="background-color: #673AB7; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Start Shopping
                    </a>
                </div>

                <p>Happy shopping!</p>
            </div>
        </body>
        </html>
        """

        return await self.send_email(to_email, subject, html_content)


# Global email service instance
email_service = EmailService()
