# THIS CODE IS UNSUPPORTED.  USE AT YOUR OWN RISK!  RACKSPACE SUPPORT WILL NOT BE ABLE TO TROUBLESHOOT OR RECOVER VOLUMES DELETED BY THIS SCRIPT.
#!/bin/env python
import cinderclient.client as cinder
from datetime import datetime
from functools import cmp_to_key
import sys
import os
import datetime
import smtplib
import time
import logging
import logging.handlers
from email.mime.text import MIMEText

mail_rcpt = "<insert email address here>"
mail_from = "<insert mail from address here>"
mail_server = "insert smtp server here"
response = ""
response2 = ""

today = datetime.date.today()
keep = today - datetime.timedelta(days=7)

if "CINDER_RAX_AUTH" not in os.environ:
    os.environ["CINDER_RAX_AUTH"] = "1"
conn = cinder.Client("1", "insert username here",
    "insert password here",
    tenant_id=insert tenant id here,
    region_name="insert region here",
    auth_url="https://identity.api.rackspacecloud.com/v2.0/",
    )


volumes = conn.volumes.list()
snapshots = conn.volume_snapshots.list()

for volume in volumes:
    try:
        for snapshot in snapshots:
            #print(volume.id, snapshot.id)
            start_time = datetime.datetime.strptime(snapshot.created_at[:-16], '%Y-%m-%d')
            if start_time.date() < keep:
                print('Deleting snapshots %s' % snapshot.id)
                snapshot.delete()
                response = response + '\n\nDeleting snapshot %s\n' % snapshot.id
                time.sleep(60)
    except:
        pass
for volume in volumes:
    try:
        snap = conn.volume_snapshots.create(volume.id, force=True)
        print('Snapshotting %s' % volume.display_name)
        response2 = response2 + '\n\nSnapshotting %s\n' % volume.display_name
    except:
        pass


def date_compare(snap1, snap2):
    if snap1.start_time > snap2.start_time:
        return -1
    elif snap1.start_time == snap2.start_time:
        return 0
    return 1

message = MIMEText ( response + response2 )
message["Subject"] = "Snapshot Monitoring %s " % start_time.date()
message["From"] = mail_from
message["To"] = mail_rcpt
smtpObj = smtplib.SMTP( mail_server )
smtpObj.sendmail(mail_from, mail_rcpt, message.as_string())
smtpObj.quit()
