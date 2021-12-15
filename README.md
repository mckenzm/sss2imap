# sss2imap
push email rulesaved in S3 to an IMAP folder, for another account even.

So, you will have to manually create a rule in SES for each email?
Can try for domain and make it catch all?

My preference is to have 2 or three private values and separate them by folder name.
It may be an idea to create the folder first, there is a risk it is removed with the last email otherwise.
Regardless, leave the AMAZON message in there as a sentinel. - maybe manually download if you have to.

You can always binsort on the client in any case. In this way, you can have SES for outbound messages from an arbitrary utility mailing identity.
Then customise the REPLY TO. Voila! -unlimited private components on a domain name and a catch-all processor.

Caveat. Yes SES allows you to send email from a domain, but without a mail account that copy might not be saved.
It does not matter if you are always sending to yourself or something you control. BCC otherwise?

2nd preference is to pay for one email in Workmail, and receive a number of addresses to it. Clients can filter.

This is a good starting point in any case.

**To consider.**

The process will fetch tranches of up to 999 emails, currently it does not repeat to empty (bar 1) the bucket.
It always fetches the sentinel.
Locking is not considered. There should only be one client?
Nor does it report 1000 records were fetched. Counters then.
Better logging.
Arguments.
Separately def'd function for the "secrets" from a config file.
/etc  integration, man page - all beyond the scope of a proof of concept.
Re-write in bash? in C?
