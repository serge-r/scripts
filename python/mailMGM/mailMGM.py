#!/usr/bin/env python

import os, sys
import argparse
import random
import subprocess
import smtplib   
from email.mime.text import MIMEText    

MAILBOX_DIR = "./mailDir"
MAILCONFIG_DIR = "./mailConf"
PASS_LEN=12
CRYPT_SCHEME="SHA512-CRYPT"

POSTMASTER_ADDRESS="postmaster@localhost"
SMTP_SERVER="localhost"
SUBJECT="Welcome"
TEXT="Welcome" + user +" to " + domain + "!!!"

result = {}

def randomPass(len=PASS_LEN):
	""" Creates and return random string """
	digits = "0123456789"
	liters = "abcdefghijklmnopqrstuvwxyz+--()"
	upLiters = liters.upper()

	literList = list(liters + digits + upLiters)
	random.shuffle(literList)
	password = "".join(random.choice(literList) for x in xrange(len))
	return password

def cryptUser(user, passwd):
	""" Call dovecot adm utility for create and return crypted string
	TODO: try generate string by python """
	PIPE = subprocess.PIPE
	proc = subprocess.Popen(['doveadm', 'pw', '-s', CRYPT_SCHEME, '-p', passwd],  stdout = PIPE)
	string = user + ":" + proc.communicate()[0]
	return string

def sendMail(who):
	""" Send mail to new user for creating emails dir """
	msg = MIMEText(TEXT)
	msg["Subject"] = SUBJECT
	msg["From"] = POSTMASTER_ADDRESS
	msg["To"] = who
	try:
		server = smtplib(SMTP_SERVER)
		sendmail(POSTMASTER_ADDRESS, [who], msg.as_string())
		server.quit()
		return 1
	except Exception as e:
		return 0, e

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
user, domain = args.mailaddr.lower().split("@")

# Get already created domains
# Fail if MAILCONFIG_DIR is not set 
try:
	domains = os.listdir(MAILCONFIG_DIR)
# print domains
except Exception as e:
	print "Test you MAILCONFIG_DIR variable", e 
	exit(1)

# check existent domains 
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
		os.mkdir(MAILCONFIG_DIR+"/"+domain)
		os.mkdir(MAILBOX_DIR+"/"+domain)

		open(MAILCONFIG_DIR+"/"+domain+"/passwd",'a').close()
		open(MAILCONFIG_DIR+"/"+domain+"/aliases",'a').close()
	except Exception as e:
		result[args.mailaddr] = {
			"result" : 0,
			"reason" : "domain not created",
			"error"  : e
		}
		print result
        exit(1)
        
# Get already created usernames for domain
# And create if user not exist
try:
	with open (MAILCONFIG_DIR+"/"+domain+"/passwd","r+") as passwdfile: 
		# TODO: use match or search -  
		lines = passwdfile.readlines()
		users = (line.split(":")[0] for line in lines)
		if user in users:
			# TODO: add result output
			print "user exists"
			exit(1)
		# Create user
		Pass = randomPass()
		cryptString=cryptUser(user=mail, passwd=Pass)
		print cryptString
		passwdfile.write(cryptString)
except Exception as e:
	print e
	exit(1)

