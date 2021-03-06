#!/usr/bin/env python

""" Scripts create mailboxes for exim\dovecot mailboxes
managed on this article:  http://www.lunch.org.uk/wiki/virtualmailboxeswitheximanddovecot 
"""

import os, sys
import re
import pwd
import grp
import argparse
import random
import subprocess
import smtplib
from email.mime.text import MIMEText

MAILBOX_DIR = "/var/vmail"
MAILCONFIG_DIR = "/etc/dovecot/vmail"
PASS_LEN=12
CRYPT_SCHEME="SHA256-CRYPT"
# user owned fo creating files
OWNER="vmail"

POSTMASTER_ADDRESS="postmaster@localhost"
SMTP_SERVER="localhost"
SMTP_TIMEOUT=5
SUBJECT="Welcome"
TEXT="""Welcome !!!"""

result = {}

def randomPass(len=PASS_LEN):
	""" Creates and return random string 
	Liters == letters
	"""
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
	TODO: error in mail send (??)
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

def outPut(what, code, reason):
	""" Print some message about..."""
	result[what] = {
		"result" : code,
		"reason" : reason
	}
	print result

def main():
	""" Let's start """
	# Create parser object, and adding arguments
	parser = argparse.ArgumentParser(description="Add a mailbox domain into exim+dovecot")
	parser.add_argument("mailaddr",
				help="email in user@domain format")
	parser.add_argument("-c",
				"--create",
				action="store_true",
				help="Create non-exist domains")
	args = parser.parse_args()

	# Email match regex
	# f*ck rfc822 -  http://www.ex-parrot.com/~pdw/Mail-RFC822-Address.html
	# its simple check
	mailaddr = args.mailaddr.lower()
	regex = re.compile(r"([a-z0-9])+([._-]{1}([a-z0-9])+)*@([a-z0-9])+([.-]{1}([a-z0-9])+)*$")
	if (not regex.match(mailaddr)):
		outPut(mailaddr,0,"Not valid mail address")
		exit(1)

	# Get uid and gid for owner
	try:
		uid = pwd.getpwnam(OWNER).pw_uid
		gid = grp.getgrnam(OWNER).gr_gid
	except Exception as e:
		outPut(mailaddr,0,"Cannot get user "+ OWNER + " check OWNER param " + e.strerror)
		exit(1)

	# Divide mailaddr arg into mail and domain parts
	user, domain = mailaddr.split("@")

	# Get domains and check MAILCONFIG_DIR
	try:
		domains = os.listdir(MAILCONFIG_DIR)
	except:
		outPut(mailaddr, 0, "Could not find domains - see MAILCONFIG_DIR variable")
		exit(1)

	# Check or create existent domains
	# TODO: change this govnokod
	if args.create:
		if(domain not in domains):
			try:
				# Create directories and passwd\alias files
				os.mkdir(MAILCONFIG_DIR+"/"+domain)
				os.mkdir(MAILBOX_DIR+"/"+domain)

				os.chown(MAILCONFIG_DIR+"/"+domain,uid,gid)
				os.chown(MAILBOX_DIR+"/"+domain,uid,gid)
				# Touch me)
				open(MAILCONFIG_DIR+"/"+domain+"/passwd",'a').close()
				open(MAILCONFIG_DIR+"/"+domain+"/aliases",'a').close()
				# Chown me)
				os.chown(MAILCONFIG_DIR+"/"+domain+"/passwd",uid,gid)
				os.chown(MAILCONFIG_DIR+"/"+domain+"/aliases",uid,gid)
			except Exception as e:
				outPut(mailaddr, 0, "Domain not create - check rigths or exists folders " + e.strerror)
				exit(1)
	else:
		if (domain not in domains):
			outPut(mailaddr, 0, "Domain not exists")
	 		exit(1)
	        
	# Get already created usernames for domain
	# And create if user not exist
	try:
		with open (MAILCONFIG_DIR+"/"+domain+"/passwd","r+") as passwdfile: 
			# Check exists users
			lines = passwdfile.readlines()
			users = (line.split(":")[0] for line in lines)
			if user in users:
				outPut(mailaddr, 0, "User exists")
				exit(1)
			# Create user
			Pass = randomPass()
			cryptString=cryptUser(user, Pass)
			passwdfile.write(cryptString)
			# Try to send mail for creating mailbox
			if sendMail(mailaddr):
				# f*ck, I forget for password =(
				result[mailaddr] = {
					"result" : 1,
					"reason" : 'User successfully created',
					"password" : Pass
				}
				print(result)
			else:
				outPut(mailaddr, 0,	"Cannot send mail to user, check smtp server")
				exit(1)
			exit(0)
	except Exception as e:
		outPut(mailaddr, 0, "User not created - some error in passwd file or mail-server:" + e.strerror)
		exit(1)

if __name__ == '__main__':
    main()