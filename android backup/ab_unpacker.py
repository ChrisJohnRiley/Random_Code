#!/usr/bin/python
# -*- coding:utf8 -*-


# 
# ab_unpacker.py (Android Backup Unpacker)
#
# Performs adb backup of an android application and decompresses
#

import pexpect
import optparse
import sys
import os

def main():

    	usage = "\n%prog [options] arguments"
	version = "v1.0 - @ChrisJohnRiley"
	logo(version)
    	
	parser = optparse.OptionParser(usage=usage, version=version)

    	parser.add_option("-p", "--package", dest="package", help="Android Package to backup")
	parser.add_option("-b", "--backfile", dest="backfile", help="Backup destination filename")
	parser.add_option("-l", "--list", dest="list", help="Create Tar List file for repacking", action="store_true")

    	(opts, args) = parser.parse_args()

	if opts.package and opts.backfile:
		print("\n [ ] Starting script to backup %s to %s") % (opts.package, opts.backfile)
	else:
		print("\n [X] Required arguements [package] and [backfile] not provided\n")
		parser.print_help()
		print("\n")
		sys.exit(0)

	(adbbackup, unpackdir) = setup(opts.package, opts.backfile)
	checks(opts.backfile, unpackdir)
	backup(adbbackup, opts.backfile)
	decode(unpackdir, opts.backfile)
	if opts.list:
		create_list(unpackdir)
	extract(unpackdir)
	
	print("\n [ ] Script completed...\n\n")

def logo(version):
	print('''
       _                                  _             
      | |                                | |            
  __ _| |__  _   _ _ __  _ __   __ _  ___| | _____ _ __ 
 / _` | '_ \| | | | '_ \| '_ \ / _` |/ __| |/ / _ \ '__|
| (_| | |_) | |_| | | | | |_) | (_| | (__|   <  __/ |   
 \__,_|_.__/ \__,_|_| |_| .__/ \__,_|\___|_|\_\___|_|   
         ______         | |                             
        |_/_//_|        |_|   %s''') % version

def setup(package, backfile):
	
	# setup variables for the script
	adbbackup = 'adb backup ' + package + ' -f ' + backfile
	unpackdir = package

	return (adbbackup, unpackdir)

def checks(backfile, unpackdir):

	# check if file and/or directory exist already
	if os.path.exists(backfile):
		print(" [X] Target of backup: %s already exists") % backfile
		sys.exit(1)

	if os.path.exists(unpackdir):
		print(" [X] Target directory: %s already exists") % unpackdir
		sys.exit(1)

	# check openssl zlib support
	child = pexpect.spawn ('openssl -help')
	i = child.expect ('zlib')

	if i==1:
		print(" [X] Openssl Version does not support zlib")
		sys.exit(1)

def backup(adbbackup, backfile):

	# backup application over adb
	print(" [ ] Running Android Backup: %s") % adbbackup

	print(" [>] Accept backup prompt on Android device to continue...")
	child = pexpect.spawn (adbbackup)
	for line in child:
	    print line

	# check if backup was created
	child = pexpect.spawn ('ls ' + backfile)
	i = child.expect (backfile)

	if i==0:
		if os.stat(backfile).st_size==0:
			print(" [X] Resulting Android Backup file is empty - check application name")
			sys.exit(1)	
		else:
			print("\n [ ] Android Backup file (%s) created") % backfile
	else:
		print(" [X] Error creating Android Backup file")
		sys.exit(1)

def decode(unpackdir, backfile):

	# decode Android Backup using dd and openssl zlib
	print(" [ ] Creating directory %s and unpacking Android Backup (%s)") % (unpackdir, backfile)

	# create directory
	os.mkdir(unpackdir)

	# convert ab to tar
	child = pexpect.spawn ('/bin/bash -c "dd if=' + backfile + ' bs=24 skip=1 | openssl zlib -d > ' + unpackdir + '.tar"')
	i = child.expect('records out')

	if i==1:
		print(" [X] Unable to decompress Android Backup file (%s)") % backfile
		sys.exit(1)

	if not os.path.exists(unpackdir + '.tar'):
		print(" [X] Unable to create TAR file (%s)") % (unpackdir + '.tar')
		sys.exit(1)

def create_list(unpackdir):

	# create list from TAR file (for use in repacking)
	print(" [ ] Creating filelist from TAR file (%s)") % (unpackdir + '.list')
	child = pexpect.spawn ('/bin/bash -c "tar -tf ' + unpackdir + '.tar > ' + unpackdir + '.list"')


def extract(unpackdir):

	# extract tar to destination directory
	child = pexpect.spawn ('tar -xvf' + unpackdir + '.tar -C' + unpackdir +'/')
	print("\n [>] Expanding Android Backup (TAR) to ./%s\n") % unpackdir
	for line in child:
	    if not line.startswith("/bin/tar:"):
		# print non-informational lines		
		print(" [>] Creating: ./%s/%s") % (unpackdir, line),


if __name__ == "__main__":
   main()

