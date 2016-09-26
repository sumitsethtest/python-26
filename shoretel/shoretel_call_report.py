#!/usr/bin/env python

'''
Title: Shoretel Call Report generator
Author: Chris Gleason
Synopsis: This script will poll the TmsNcc logs on a designated
          Shoretel DVS system so you can see all calls relating
          to that username or SIP IP (or whatever search string
          you want to use that will be unique to each call 
          creation event C-CE

          As well it will poll the IPBX log to pull BYE codes
          per call.

Future Work: I'm planning on expanding this to Twilio as well
             so we can cross reference Twilio logs with 
             Shoretel logs as well, but need to read up on the
             API first.

'''


# IMPORTS HERE

import sys
import subprocess

if len(sys.argv) == 1:
    print
    print "Usage: The script takes five arguments:"
    print "       1) The username you want to authenticte to the SMB share on the DVS"
    print "       2) The specific TmsNcc log file name you want to parse"
    print "       3) The specific IPBX log file name you want to parse"
    print "       4) The IP of the DVS server you want to mount"
    print "       5) The term you want to search for (SIP IP, Username, etc)"
    print "       in that order"
    print
    print "For the search term, use the IP of the Phone or the username if that fails. You can also use a CALL-ID if you want just that."
    print
    print "Example: shoretel_call_report.py cgleason TmsNcc-160531.000001.Log IPBX-160531.000001 172.17.68.13 Ophelie"
    print
    exit (0)

# Globally used Variables

user = str(sys.argv[1])
log = str(sys.argv[2])
log2 = str(sys.argv[3])
dvs_server = str(sys.argv[4])
term = str(sys.argv[5])
mount_cmd = "mkdir /Volumes/dvs && mount -t smbfs //%s@%s/c$ /Volumes/dvs" % (user,dvs_server)

subprocess.call(mount_cmd, shell=True)

# PULL IPBX LOG AND CREATE A DICTIONARY OUT OF IT

bye_list_cmd = "cat /Volumes/dvs/Shoreline\ Data/Logs/%s | egrep 'BYE' | cut -d '=' -f2" % (log2)
cid_list_cmd = "cat /Volumes/dvs/Shoreline\ Data/Logs/%s | egrep 'CALL-ID' | cut -d ',' -f1 | cut -d ' ' -f 5" % (log2)

bye_list = subprocess.Popen(bye_list_cmd, shell=True, stdout=subprocess.PIPE)
bye_list = bye_list.stdout.read()
cid_list = subprocess.Popen(cid_list_cmd, shell=True, stdout=subprocess.PIPE)
cid_list = cid_list.stdout.read()

concat = dict(zip(cid_list.split(), bye_list.split()))

#for x,y in concat.items():
#    if x == stripped_cid:
#        print x,y

#print concat

#PULL FROM TMSNCC LOG AND INCLUDE CALL BYE CODE FROM IPBX

# Variable assignments for TmsNCC log here

encap_cmd = "cat /Volumes/dvs/Shoreline\ Data/Logs/%s | egrep \"L-IE|C-CE|L-DE\" | grep \"%s\" | awk '{print $7}' | cut -d '\"' -f 2 | sort | uniq | grep -e '[^\ ]\{30,\}'" % (log,term)


id_list = subprocess.Popen(encap_cmd, shell=True, stdout=subprocess.PIPE)
id_list = id_list.stdout.read().split('\n')
id_list = filter(None, id_list)


for i in id_list:
    id = i
    stripped_cid = id.replace("-","").lstrip("0")
    stripped_cid = "0"+stripped_cid
    grep_log1_cmd = "cat /Volumes/dvs/Shoreline\ Data/Logs/{} | grep '{}'".format(log,id)
    call = subprocess.Popen(grep_log1_cmd, shell=True, stdout=subprocess.PIPE)
    call = call.stdout.read()
    print
    print
    print "============================================"
    print "CALL ID " + id
    print "============================================"
    print
    print call
    print "........................................"
    print "BYE code is: " + concat[stripped_cid]
    print "........................................"

print
print "REPORT COMPLETE!"
print

subprocess.call("umount /Volumes/dvs", shell=True)


