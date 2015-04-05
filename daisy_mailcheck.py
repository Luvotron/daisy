#!/usr/bin/python3

#Daisy mail checker

import configparser, os, imaplib, email, time

class Settings:
    def __init__(self):
        #load the goodies
        config = configparser.ConfigParser()
        config.read('daisy_comm.conf')
        self.server = config['Email']['server']
        self.port   = config.getint('Email', 'port')
        self.username = config['Email']['username']
        self.password = config['Email']['password']
        self.senders = config['General']['senders']

if __name__=="__main__":
    settings = Settings()

    mail = imaplib.IMAP4(settings.server)
    mail.login(settings.username, settings.password)
    
    mail.select('Inbox')
    result, data = mail.uid('search', None, 'ALL')

    i = len(data[0].split())
    for x in range(i):
        latest_uid = data[0].split()[x]
        result, email_data = mail.uid('fetch', latest_uid, '(RFC822)')
        raw_email = email_data[0][1]
        raw_email = raw_email.decode('utf-8')
        email_msg = email.message_from_string(raw_email)
        email_from = email_msg['from']
        email_from = email_from[email_from.find('<') + 1:email_from.find('>')]
        
        for part in email_msg.walk():
            if email_from in settings.senders and part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                filename = str('txt/email_' + str(time.time()) + '.txt')
                savefile = open(filename, 'a')
                savefile.write(body.decode('utf-8'))
                savefile.close()
                #move to Seen folder
                mail.uid('copy', latest_uid, 'Inbox.Seen')
                mail.uid('store', latest_uid, '+FLAGS', '\\Deleted')

            elif not(email_from in settings.senders):
                #move to Alien folder
                mail.uid('copy', latest_uid, 'Inbox.Alien')
                mail.uid('store', latest_uid, '+FLAGS', '\\Deleted')

            else:
                continue

        

    mail.close()
    mail.logout()
    #print(num)
    print ('disconnected')
