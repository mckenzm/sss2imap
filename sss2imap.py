#!/usr/bin/python3
"""
    Pop RFC822 objects from S3 and push them to an IMAP folder.
    Objects have previously been saved to an S3 folder by an SES received email rule. 
    
    https://stackoverflow.com/a/30262449/1734032
    https://docs.python.org/3/library/imaplib.html

    Needs config file. 
    Intended as a catch-all solution, could modify to scan for folders, but binsort can be done on the clientside.
    Care to create folder before SES rules, if first email creates, last removes it?.. 
    Code currently considers SES confirmation message as a sentinel, to only be downladed manually and never deleted.
    
"""
from io           import BytesIO
from boto3        import client
from imaplib      import IMAP4_SSL
from email.parser import BytesParser, Parser
from email.policy import default
from datetime     import datetime

bucketName  = ""                   #maybe fn() to read from a config file to load these up.
prefixName  = ""                   #enhancement to loop on each found is nice to have. 
imapUser    = ""
imapPass    = ""
imapHost    = ""
imapPort    = 993                #default for SSL, important if different  
imapMailbox = "INBOX"

dateTimeObj = datetime.now()
timestampStr = dateTimeObj.strftime("%Y-%m-%d-%H.%M.%S.%f")
# print("Invoked", timestampStr)

conn = client('s3')  # assumes boto.cfg setup, assume AWS S3
bytes_buffer = BytesIO()

with IMAP4_SSL(host=imapHost,port=imapPort) as M:
#   print("Logging on to IMAP server...")
    M.login(imapUser,imapPass)
#   print("Selecting mailbox...")
    M.select(mailbox=imapMailbox,readonly=False)

    finished = False
    count    = 0
    total    = 0

    while not finished:

#       print("Fetching from S3 bucket...")
#       print("*")

        for key in conn.list_objects(Bucket=bucketName, Prefix=prefixName)['Contents']:  # max 1000, but running frequently.

            count = count + 1
            if 'AMAZON' not in key['Key']:   # leave or the above crashes if folder removed.
                total = total + 1
                conn.download_fileobj(Bucket=bucketName, Key=key['Key'], Fileobj=bytes_buffer)
                byte_value = bytes_buffer.getvalue()                                     # stay in bytes, no need to .decode()
                headers = BytesParser(policy=default).parsebytes(byte_value,headersonly=True)
                print('Date   : {}'.format(headers['date']))
                print('To     : {}'.format(headers['to']))
                print('From   : {}'.format(headers['from']))
                print('Subject: {}'.format(headers['subject']))
                print('*')
                rc = M.append(imapMailbox,'','',byte_value)        #send it, should really test in case of quota.

                # check response from above? Delete from bucket.
                if rc[0] == 'OK':
                    conn.delete_object(Bucket=bucketName, Key=key['Key'])

        if count < 1000:
            finished = True
            count    = 0

#   print("Logging off...")
#   print("-----------------------------------")
    M.close()
    M.logout()
