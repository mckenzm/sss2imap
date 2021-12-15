#!/usr/bin/python3
""" 
    https://stackoverflow.com/a/30262449/1734032
    https://docs.python.org/3/library/imaplib.html
    
    Need args. Parametise the change-ey things like prefix or probe for all prefixes (major enhancement and new loop ?)
    care to create folder, if first email creates, last removes it? .. or leave SES message as sentinel.
    Need also to check append response.
"""
from io           import BytesIO 
from boto3        import client
from imaplib      import IMAP4_SSL
from email.parser import BytesParser, Parser
from email.policy import default

bucketName  = ""                   #maybe fn() to read from a config file to load these up.
prefixName  = ""                   #enhancement to loop on each found is nice to have. 
imapUser    = ""
imapPass    = ""
imapHost    = ""
imapPort    = "993"
imapMailbox = "INBOX"

conn = client('s3')  # assumes boto.cfg setup, assume AWS S3
bytes_buffer = BytesIO()

with IMAP4_SSL(host=imapHost,port=imapPort) as M:
    M.login(imapUser,imapPass)
    M.select(mailbox=imapMailbox,readonly=False)

    for key in conn.list_objects(Bucket=bucketName, Prefix=prefixName)['Contents']:  # max 1000, but running frequently.
        if 'AMAZON' not in key['Key']:                                             # leave or the above crashes if folder removed.
            conn.download_fileobj(Bucket=bucketName, Key=key['Key'], Fileobj=bytes_buffer)
            byte_value = bytes_buffer.getvalue()                                     # stay in bytes, no need to .decode()
            headers = BytesParser(policy=default).parsebytes(byte_value,headersonly=True)
            print('Date   : {}'.format(headers['date']))
            print('To     : {}'.format(headers['to']))
            print('From   : {}'.format(headers['from']))
            print('Subject: {}'.format(headers['subject']))
            print(' ')
            M.append(imapMailbox,'','',byte_value)        #send it, should really test in case of quota.               
            # check response from above? Delete from bucket.
            conn.delete_object(Bucket=bucketName, Key=key['Key'])
        
    M.close()
    M.logout()

