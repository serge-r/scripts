#!/usr/bin/env python

import os
import sys
import re
# Argument parse lib
import argparse

#MAILBOX_DIR = "/var/vmail"
MAILBOX_DIR = "./testmaildir"
#MAILCONFIG_DIR = "/etc/dovecot/vmail"
MAILCONFIG_DIR = "./testdir"

result = {}

# create parsere object
parser = argparse.ArgumentParser(description="Add a mailbox or a domain into exim+dovecot")

# Adding arguments 
parser.add_argument("mailaddr",
					help="email in user@domain format or domain")

parser.add_argument("-c",
					"--create-domains",
					action="store_true",
					help="Create non-exist domains")

args = parser.parse_args()

# Divide mailadd arg into mail and domain parts
# TODO: make a check for valid input for mail and domains
mail, domain = re.split("@",args.mailaddr)

# print "Mail is "+mail, "Domain is "+domain

# Get already created domains
# Fail if MAILCONFIG_DIR is not set 
try:
	domains = os.listdir(MAILCONFIG_DIR)
#	print domains
except Exception as e:
	print "Test you MAILCONFIG_DIR variable", e 
	exit(1)

# check existent domains 
# TODO - add "create" flag support
if domain not in domains:
	result[args.mailaddr] = {
		"result" : 0,
		"reason" : "domain is not exists"
	}
	print result
	exit(1)

# Get already created usernames for domain
try:
	with open (MAILCONFIG_DIR+"/"+domain+"/passwd","r") as passwdfile: 
		usernames = (re.split(r":",lines,maxsplit=1) for lines in passwdfile)
		# if mail in usernames:
		# 	result[args.mailaddr] = {
		# 		"result" : 0,
		# 		"reason" : "user "+mail+" is exists"
		# 	}
		for name in usernames:
			print name[0]
except Exception as e:
	print e
	exit(1)
