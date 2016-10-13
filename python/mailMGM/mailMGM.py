#!/usr/bin/env python

""" Scripts create mailboxes for exim\dovecot mailboxes
managed on this article:  http://www.lunch.org.uk/wiki/virtualmailboxeswitheximanddovecot 
"""

import os, sys, re
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
SMTP_TIMEOUT=5
SUBJECT="Welcome"
TEXT="""Welcome !!!"""

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

def cryptUser(user, passwd,crypt_scheme=CRYPT_SCHEME):
	""" Call dovecot adm utility for create and return crypted string
	TODO: add check if dovecot is not exists
	TODO: try generate string by python """
	PIPE = subprocess.PIPE
	proc = subprocess.Popen(['doveadm', 'pw', '-s', crypt_scheme, '-p', passwd],  stdout = PIPE)
	string = user + ":" + proc.communicate()[0]
	return string

def sendMail(to, timeout=SMTP_TIMEOUT):
	""" Send mail to new user for creating emails dir
	TODO: error in connection
	"""
	msg = MIMEText(TEXT)
	msg["Subject"] = SUBJECT
	msg["From"] = POSTMASTER_ADDRESS
	msg["To"] = to
	try:
		server = smtplib.SMTP(SMTP_SERVER,timeout=timeout)
		server.sendmail(POSTMASTER_ADDRESS, [to], msg.as_string())
		server.quit()
		return True
	except:
		return False

def main():
	""" Let's start """
	# Create parser object, and adding arguments
	parser = argparse.ArgumentParser(description="Add a mailbox or a domain into exim+dovecot")
	parser.add_argument("mailaddr",
				help="email in user@domain format or domain")
	parser.add_argument("-c",
				"--create",
				action="store_true",
				help="Create non-exist domains")
	args = parser.parse_args()

	# Email match regex
	# No http://www.ex-parrot.com/~pdw/Mail-RFC822-Address.html
	# its simple check
	mailaddr = args.mailaddr.lower()
	regex = re.compile(r"([a-z0-9])+([._-]{1}([a-z0-9])+)*@([a-z0-9])+([.-]{1}([a-z0-9])+)*$")
	if (not regex.match(mailaddr)):
		result[mailaddr] = {
			"result" : 0,
			"reason" : "Not valid email address"
		}
		print result
		exit(1)

	# Divide mailaddr arg into mail and domain parts
	# TODO: make a check for valid input for mail and domains
	user, domain = mailaddr.split("@")

	# Get domains and check MAILCONFIG_DIR
	try:
		domains = os.listdir(MAILCONFIG_DIR)
	except:
		result[mailaddr] = {
			"result" : 0,
			"resaon" : "Could not find domains - see MAILCONFIG_DIR variable"
		}
		print (result)
		exit(1)

	# Check or create existent domains
    if (args.create):
	    try:
		    # Create directories and passwd\alias files
			os.mkdir(MAILCONFIG_DIR+"/"+domain)
			os.mkdir(MAILBOX_DIR+"/"+domain)
			# Touch me)
			open(MAILCONFIG_DIR+"/"+domain+"/passwd",'a').close()
			open(MAILCONFIG_DIR+"/"+domain+"/aliases",'a').close()
		except Exception as e:
		    result[mailaddr] = {
				"result" : 0,
				"reason" : "Domain not created-"+e 
		    }
			print(result)
	        exit(1)
    else:
	 	if (domain not in domains):
	 		result[mailaddr] = {
	 			"result" = 0,
	 			"reason" = "Domain not exists"
	 		}
	 		print(result)
	 		exit(1)
	        
	# Get already created usernames for domain
	# And create if user not exist
	try:
		with open (MAILCONFIG_DIR+"/"+domain+"/passwd","r+") as passwdfile: 
			# TODO: use match or search -
			lines = passwdfile.readlines()
			users = (line.split(":")[0] for line in lines)
			if user in users:
				result[mailaddr] = {
					"result" : 0,
					"reason" : "User exists"
				}
				print(result)
				exit(1)
			# Create user
			Pass = randomPass()
			cryptString=cryptUser(user=user, passwd=Pass)
			passwdfile.write(cryptString)
			# Try to send mail for creating mailbox
			if sendMail(mailaddr):
				result[mailaddr] = {
					"result" : 1,
					"reason" : "User succesfully created",
					"password" : Pass
				} 
				print(result)
			else:
				result[mailaddr]= {
					"result" : 0,
					"reason" : "Cannot send mail to user, check smtp server"
				}
				print(result)
				exit(1)
			exit(0)
	except Exception as e:
		result[mailaddr] = {
			"result" : 0,
			"reason" : "User not created - some error in passwd file or mail-server: "+e
		}
		print(result)
		exit(1)

if __name__ == '__main__':
    main()
