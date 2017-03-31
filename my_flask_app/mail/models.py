from flask_mail import Message
from flask import render_template
from flask import current_app
from .. import mail


class EmailMessage:
    def __init__(self, subject=None, recipients=None):
        self.sender = current_app.config['MAIL_SENDER']
        self.subject = subject
        self.recipients = recipients
        self.body = None
        self.html = None

    def set_template(self, template, **kwargs):
        self.body = render_template(template + ".txt", **kwargs)
        self.html = render_template(template + ".html", **kwargs)

    def send(self, with_prefix=True):
        if with_prefix:
            subject = current_app.config['MAIL_PREFIX'] + "  " + self.subject
        else:
            subject = self.subject
        msg = Message(
            subject,
            sender=self.sender,
            recipients=self.recipients
        )
        msg.body = self.body
        msg.html = self.html
        return mail.send(msg)
