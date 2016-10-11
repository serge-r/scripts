#!/usr/bin/env python

import os, sys, re
# Argument parse lib
import argparse
import random

#MAILBOX_DIR = "/var/vmail"
MAILBOX_DIR = "/home/candidate/repos/scripts/python/mailMGM/testmaildir"
#MAILCONFIG_DIR = "/etc/dovecot/vmail"
MAILCONFIG_DIR = "/home/candidate/repos/scripts/python/mailMGM/testdir"

result = {}

# create parser object
parser = argparse.ArgumentParser(description="Add a mailbox or a domain into exim+dovecot")

# Adding arguments 
parser.add_argument("mailaddr",
					help="email in user@domain format or domain")

parser.add_argument("-c",
					"--create",
					action="store_true",
					help="Create non-exist domains")

args = parser.parse_args()

# Divide mailadd arg into mail and domain parts
# TODO: make a check for valid input for mail and domains
# TODO: make all lowercase
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
if (domain not in domains) and not args.create:
	result[args.mailaddr] = {
		"result" : 0,
		"reason" : "domain is not exists"
	}
	print result
	exit(1)
elif(args.create):
	try:
		# Create directories and passwd\alias files
		os.mkdir("MAILCONFIG_DIR"+"/"+domain)
		os.mkdir("MAILBOX_DIR"+"/"+domain)

		open("MAILCONFIG_DIR"+"/"+domain+"/passwd",'a').close()
		open("MAILCONFIG_DIR"+"/"+domain+"/aliases",'a').close()
	except Exception as e:
		result[args.mailaddr] = {
			"result" : 0,
			"reason" : "domain not created",
			"error"  : e
		}
		print result

# Get already created usernames for domain
try:
	with open (MAILCONFIG_DIR+"/"+domain+"/passwd","r") as passwdfile: 
		# TODO: use match or search - 
		usernames = (re.split(r":",lines,maxsplit=1) for lines in passwdfile)

except Exception as e:
	print e
	exit(1)

# Check if user is exist
for name in usernames:
	if mail == name[0]:
		result[args.mailaddr] = {
			"result" : 0,
			"reason" : "user "+mail+" is exists"
		}
		print result
		exit(1)


# create user
