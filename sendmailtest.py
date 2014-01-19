from sendgrid import Sendgrid
from sendgrid import Message

def sendmail():

    #connection to sendgrid
    s = sendgrid.Sendgrid('gardnerb', 'HACKA_th0n')

    #make message object
    msg = sendgrid.Message("test@textbookloop.com", "test email subject",
        "Hello, this is a test e-mail, wahoo!!!","<strong> see what happens? </strong>")

    message.add_to("brad@brvth.com", "Brad Johnson")

    s.web.send(msg)
