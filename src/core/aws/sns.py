from email.mime import multipart, text
from string import Template
from typing import List

import boto3
from botocore.exceptions import ClientError, EndpointConnectionError
from pydantic import EmailStr


class AWSConnectionHandler(object):
    def __init__(
        self, resouce_type: str, access_key: str, secret_key: str, region_name: str
    ):
        self.client = boto3.client(
            resouce_type,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name,
        )


class SESHandler(AWSConnectionHandler):
    def __init__(
        self,
        access_key: str,
        secret_access: str,
        region_name: str,
        default_from_email: str,
    ):
        super(SESHandler, self).__init__(
            "ses",
            access_key=access_key,
            secret_key=secret_access,
            region_name=region_name,
        )
        self.default_from_email = default_from_email

    def send_email(
        self,
        subject: str,
        email_to_list: List,
        from_email: EmailStr = None,
        email_body_text: str = None,
        email_body_html: str = None,
        email_cc_list: List = None,
        email_bcc_list: List = None,
    ):
        if email_bcc_list is None:
            email_bcc_list = []
        if email_cc_list is None:
            email_cc_list = []
        # The email body for recipients with non-HTML email clients.
        # email_body_text = "email body text here"  # The HTML body of the email.
        # email_body_html = "email html contents"
        # The character encoding for the email.
        email_msg = multipart.MIMEMultipart("mixed")
        # Add subject, from and to lines.
        email_msg["Subject"] = subject
        email_msg["From"] = from_email or self.default_from_email
        email_msg["To"] = ", ".join(email_to_list)
        email_msg["Cc"] = ", ".join(email_cc_list)
        email_msg["Bcc"] = ", ".join(email_bcc_list)
        email_msg_body = multipart.MIMEMultipart("alternative")
        email_charset = "UTF-8"
        textpart = text.MIMEText(email_body_text, _charset=email_charset)
        htmlpart = text.MIMEText(email_body_html, "html", email_charset)
        # Add the text and HTML parts to the child container.
        email_msg_body.attach(textpart)
        email_msg_body.attach(htmlpart)
        # Attach the multipart/alternative child container to the multipart/mixed
        # parent container.
        email_msg.attach(email_msg_body)
        # if not os.path.exists(Attachment file):
        #     print("Attachment file does not exists")
        # else:
        #     # Define the attachment part and encode it using
        #     MIMEApplication.email_attachment = IMEApplication(open(Attachment file path, 'rb').read())
        #     file_name = Path(Attachment file path).name
        #             email_attachment.add_header('Content-Disposition',          'attachment', filename=file_name)
        #  # Add the attachment to the parent container.
        #  email_msg.attach(email_attachment)
        try:
            # Provide the contents of the email.
            response = self.client.send_raw_email(
                Source=email_msg["From"],
                Destinations=email_to_list + email_cc_list + email_bcc_list,
                RawMessage={
                    "Data": email_msg.as_string(),
                },
            )
            # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response["Error"]["Message"])
        except EndpointConnectionError as exp:
            print(exp)
        except ConnectionError as exp:
            print(exp)
        else:
            print(response["MessageId"])

    def send_email_html_file(
        self,
        subject: str,
        email_to_list: List,
        from_email: EmailStr = None,
        email_body_text: str = None,
        email_html_path: str = None,
        email_cc_list: List = None,
        email_bcc_list: List = None,
        **kwargs,
    ):
        if email_bcc_list is None:
            email_bcc_list = []
        if email_cc_list is None:
            email_cc_list = []
        with open(email_html_path, encoding="utf-8") as email_html:
            email_body_html = email_html.read()
            template = Template(email_body_html)
        return self.send_email(
            subject=subject,
            email_to_list=email_to_list,
            from_email=from_email,
            email_body_text=email_body_text,
            email_body_html=template.substitute(**kwargs),
            email_cc_list=email_cc_list,
            email_bcc_list=email_bcc_list,
        )

    def send_confirmation_email(self, to_email, **kwargs):
        self.send_email_html_file(
            subject="Thank you for choosing us",
            email_to_list=[to_email],
            email_body_text="Thank you for your purchase from keywords Project",
            email_html_path="app/templates/email_templates/confirmation.html",
            **kwargs,
        )

    def send_reminder_email(self, to_email, **kwargs):
        self.send_email_html_file(
            subject="Your cart is waiting",
            email_to_list=[to_email],
            email_body_text=" Looks like you left something behind. Return to your cart to complete your purchase",
            email_html_path="app/templates/email_templates/reminder.html",
            **kwargs,
        )

    def send_order_email(self, to_email: List[EmailStr], **kwargs):
        self.send_email_html_file(
            subject="You have new order",
            email_to_list=to_email,
            email_body_text="Order Created",
            email_html_path="app/templates/email_templates/order_email.html",
            **kwargs,
        )

    def send_otp_rest_pass_email(self, to_email, **kwargs):
        self.send_email_html_file(
            subject="keywords ProjectRest Password",
            email_to_list=[to_email],
            email_body_text=f"Your code is: {kwargs.get('otp_code')}",
            email_html_path="app/templates/email_templates/send_otp_reset_pass_email.html",
            **kwargs,
        )

    def send_otp_verification_email(self, to_email, **kwargs):
        self.send_email_html_file(
            subject="keywords ProjectVerification",
            email_to_list=[to_email],
            email_body_text=f"Your code is: {kwargs.get('otp_code')}",
            email_html_path="app/templates/email_templates/email-verification.html",
            **kwargs,
        )

    def send_coupon_code_email(self, to_email, **kwargs):
        self.send_email_html_file(
            subject="keywords ProjectCoupon",
            email_to_list=[to_email],
            email_body_text=f"Your Coupon is: {kwargs.get('coupon_code')}",
            email_html_path="app/templates/email_templates/send_coupon_code_email.html",
            **kwargs,
        )


class SNSHandler(AWSConnectionHandler):
    def __init__(
        self,
        access_key: str,
        secret_access: str,
        region_name: str,
    ):
        super(SNSHandler, self).__init__(
            "sns",
            access_key=access_key,
            secret_key=secret_access,
            region_name=region_name,
        )

    async def send_sms(self, phone_number, message: str):
        self.client.publish(PhoneNumber=phone_number, Message=message)
