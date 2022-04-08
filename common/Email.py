#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: leeyoshinari

import smtplib
import socket
from email.header import Header
from email.mime.text import MIMEText


def sendEmail(msg):
    """
     Send email
    """
    sender_name = msg['senderName']
    sender_email = msg['senderEmail']
    receiver_name = msg['receiverName']
    receiver_email = msg['receiverEmail']
    password = msg['password']

    s = "{0}".format(msg['msg'])

    message = MIMEText(s, 'plain', 'utf-8')  # Chinese required 'utf-8'
    message['Subject'] = Header(msg['subject'], 'utf-8')
    message['From'] = Header(sender_name)
    message['To'] = Header(receiver_name, 'utf-8')

    try:
        smtp = smtplib.SMTP_SSL(msg['smtp'], 465)
    except socket.error:
        smtp = smtplib.SMTP(msg['smtp'], 25)

    smtp.login(sender_email, password)
    smtp.sendmail(sender_email, receiver_email, message.as_string())
    smtp.quit()

