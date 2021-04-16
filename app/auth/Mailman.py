import smtplib
from pydantic import EmailStr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import FileSystemLoader, Environment

from app import ic
from app.settings import settings as s


class Mailman:
    host_user = s.EMAIL_HOST_USER
    host_pass = s.EMAIL_HOST_PASS
    sender = s.EMAIL_SENDER
    subject = ''
    message = {}
    
    def __init__(self, *, recipient: str):
        self.recipient = recipient
    
    def setup_email(self, *, subject: str = '', recipient: str = '',
                    sender: EmailStr = s.EMAIL_SENDER):
        message = MIMEMultipart('alternative')
        message['Subject'] = subject or self.subject
        message['From'] = sender or self.sender
        message['To'] = recipient or self.recipient
        self.message = message
        
    def get_template(self, *, text='', html=None, context=None):
        context = context or {}
        file_path, file_name = text.rsplit('/', 1)
        env = Environment(loader=FileSystemLoader(file_path))
        env.trim_blocks = True
        text_template = env.get_template(file_name)
        text = text_template.render(**context)
        self.message.attach(MIMEText(text, "plain"))

        if html:
            file_path, file_name = html.rsplit('/', 1)
            env = Environment(loader=FileSystemLoader(file_path))
            env.trim_blocks = True
            html_template = env.get_template(file_name)
            html = html_template.render(**context)
            self.message.attach(MIMEText(html, "html"))
            
    def as_str(self):
        return self.message.as_string()
    
    def send(self, *, text='', html=None, context=None):
    
        # with smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT) as server:
        #     server.sendmail(sender, recipient, message.as_string())
        
        self.get_template(text=text, html=html, context=context)
        try:
            smtp = smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT)
            # smtp.starttls()
            # smtp.login(self.host_user, self.host_pass)
            smtp.sendmail(self.sender, self.recipient, self.as_str())
            smtp.quit()
            return True
        except Exception as e:
            # TODO: What to do with this
            # ic(e)
            pass

        # server = None
        # context = ssl.create_default_context()
        # try:
        #     server = smtplib.SMTP(s.EMAIL_HOST, s.EMAIL_PORT)
        #     server.starttls(context=context)
        #     server.login(sender, passwd)
        # except Exception as e:
        #     ic(e)
        # finally:
        #     server.quit()

        # with smtplib.SMTP_SSL(s.EMAIL_HOST, s.EMAIL_PORT, context=context) as server:
        #     server.login(sender, 'foobar')
        #     server.sendmail(sender, recipient, message)
