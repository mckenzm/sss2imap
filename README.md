# sss2imap
push email rulesaved in S3 to an IMAP folder, possibly another account even.

So, you will have to manually create a rule in SES for each email?
Can try for domain and make it catch all?

My preference is to have 2 or three private values and separate them by folder name.
It may be an idea to create the folder first, there is a risk it is removed with the last email otherwise.
Regardless, leave the AMAZON message in there as a sentinel. - maybe manually download if you have to.

Caveat. Yes SES allows you to send email from a domain, but without a mail account that copy might not be saved.
It does not matter if you are always sending to yourself or something you control. BCC otherwise?

2nd preference is to pay for one email in Workmail, and receive a number of addresses to it. Clients can filter.

This is a good starting point in any case.
