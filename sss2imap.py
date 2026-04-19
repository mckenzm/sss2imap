#!/usr/bin/python3
"""
    Pop RFC822 objects from S3 and push them to an IMAP folder.
    Objects have previously been saved to an S3 folder by an SES received email rule.

    https://stackoverflow.com/a/30262449/1734032
    https://docs.python.org/3/library/imaplib.html

    Needs config file.
    Intended as a catch-all solution, could modify to scan for folders, but binsort can be done on the clientside.
    Care to create folder before SES rules, if first email creates, last removes it?..
    Code currently considers SES confirmation message as a sentinel, to only be downloaded manually and never deleted.

"""
from io           import BytesIO
from boto3        import client
from imaplib      import IMAP4_SSL, Time2Internaldate
from email.parser import BytesParser
from email.policy import default
from email.utils  import parsedate_to_datetime
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

with IMAP4_SSL(host=imapHost, port=imapPort) as M:
#   print("Logging on to IMAP server...")
    M.login(imapUser, imapPass)
#   print("Selecting mailbox...")
    M.select(mailbox=imapMailbox, readonly=False)

    for key in conn.list_objects_v2(Bucket=bucketName, Prefix=prefixName)['Contents']:

        if 'AMAZON' not in key['Key']:   # leave sentinel or the above crashes if folder removed.
            bytes_buffer = BytesIO()
            conn.download_fileobj(Bucket=bucketName, Key=key['Key'], Fileobj=bytes_buffer)
            byte_value = bytes_buffer.getvalue()
            msg = BytesParser(policy=default).parsebytes(byte_value)
            print('Date   : {}'.format(msg['date']))
            print('To     : {}'.format(msg['to']))
            print('From   : {}'.format(msg['from']))
            print('Subject: {}'.format(msg['subject']))

            body_part = msg.get_body(preferencelist=('plain',))
            if body_part:
                text = body_part.get_content().strip()
                if text:
                    print('\n'.join(text.splitlines()[:10]))
            print('*')

            try:
                imap_date = Time2Internaldate(parsedate_to_datetime(msg['date'])) if msg['date'] else None
            except Exception:
                imap_date = None

            rc = M.append(imapMailbox, '', imap_date, byte_value)   #send it, should really test in case of quota.

            # check response from above? Delete from bucket.
            if rc[0] == 'OK':
                conn.delete_object(Bucket=bucketName, Key=key['Key'])

#   print("Logging off...")
#   print("-----------------------------------")
    M.close()
    M.logout()
