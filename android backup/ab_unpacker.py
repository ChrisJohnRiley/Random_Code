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
import errno

def main():

	usage = "\n%prog [options] arguments"
	version = "v1.1 - @ChrisJohnRiley"
	logo(version)

	parser = optparse.OptionParser(usage=usage, version=version)

	parser.add_option("-p", "--package", dest="package", help="Android Package to backup")
	parser.add_option("-b", "--backfile", dest="backfile", help="Backup destination filename")
	parser.add_option("-u", "--unpackdir", dest="unpackdir", help="Optional: Unpack destination")
	parser.add_option("-l", "--list", dest="list", help="Create Tar List file for repacking", action="store_true")
	parser.add_option("-a", "--apk", dest="apk", help="Include APK in backup", action="store_true")
	parser.add_option("-v", "--verbose", dest="verbose", help="Verbose output", action="store_true")
	parser.add_option("-o", "--overwrite", dest="overwrite", help="Overwrite files/directories", action="store_true")

	global opts
	(opts, args) = parser.parse_args()


	if opts.package and opts.backfile:
		print("\n [ ] Starting script to backup %s to %s") % (opts.package, opts.backfile)
	else:
		print("\n [X] Required arguements [package] and [backfile] not provided\n")
		parser.print_help()
		print("\n")
		sys.exit(0)

	if opts.overwrite:
		print("\n [!] Overwriting enabled -\n")
		print("\t - existing backup data will be overwritten")
		print("\t - existing files within the unpack directory will be overwritten\n")

	setup()
	checks()
	backup()
	decode()
	if opts.list:
		create_list()
	extract()
	if opts.verbose:
		# output summary of extracted files
		summary()

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

def setup():

	# setup variables for the script
	opts.adbbackup = 'adb backup ' + opts.package + ' -f ' + opts.backfile
	if opts.apk:
		# add apk to backup
		opts.adbbackup = opts.adbbackup + ' -apk'
	if not opts.unpackdir:
		# set backup directory to pacakge name
		opts.unpackdir = opts.package

def checks():

	if not opts.overwrite:

		# check if file and/or directory exist already
		if os.path.exists(opts.backfile):
			print(" [X] Target of backup: %s already exists\n") % opts.backfile
			sys.exit(1)
	
		if os.path.exists(opts.unpackdir):
			print(" [X] Target directory: %s already exists\n") % opts.unpackdir
			sys.exit(1)

	# check openssl zlib support
	child = pexpect.spawn ('openssl -help')
	i = child.expect ('zlib')

	if i==1:
		print(" [X] Openssl Version does not support zlib")
		sys.exit(1)

def backup():

	# backup application over adb
	print(" [ ] Running Android Backup: %s") % opts.adbbackup

	print(" [>] Accept backup prompt on Android device to continue...\n")
	child = pexpect.spawn (opts.adbbackup)
	# check if adb errored out - can't use expect due to stderr?
	for line in child:
		if "unable to connect for backup" in line:
			print(" [X] ADB is unable to detect an Android device - cancelling backup\n")
			sys.exit(1)
		else:
			print line,

	# check if backup was created
	child = pexpect.spawn ('ls ' + opts.backfile)
	i = child.expect (opts.backfile)

	if i==0:
		if os.stat(opts.backfile).st_size < 42:
			print(" [X] Resulting Android Backup file is empty - check application name")
			sys.exit(1)	
		else:
			print("\n [ ] Android Backup file (%s) created") % opts.backfile
	else:
		print(" [X] Error creating Android Backup file")
		sys.exit(1)

def decode():

	# decode Android Backup using dd and openssl zlib
	print(" [ ] Creating directory %s and unpacking Android Backup (%s)") % (opts.unpackdir, opts.backfile)

	# create directory if it doesn't already exist
	if not os.path.exists(opts.unpackdir):
		os.mkdir(opts.unpackdir)

	# convert ab to tar
	child = pexpect.spawn ('/bin/bash -c "dd if=' + opts.backfile + ' bs=24 skip=1 | openssl zlib -d > ' + opts.backfile + '.tar"')
	i = child.expect('records out')

	if i==1:
		print(" [X] Unable to decompress Android Backup file (%s)") % opts.backfile
		sys.exit(1)

	if not os.path.exists(opts.backfile + '.tar'):
		print(" [X] Unable to create TAR file (%s)") % (opts.backfile + '.tar')
		sys.exit(1)

def create_list():

	# create list from TAR file (for use in repacking)
	print(" [ ] Creating filelist from TAR file (%s)") % (opts.backfile + '.tar.list')
	child = pexpect.spawn ('/bin/bash -c "tar -tf ' + opts.backfile + '.tar > ' + opts.backfile + '.tar.list"')

def extract():

	# extract tar to destination directory
	child = pexpect.spawn ('tar -xvf' + opts.backfile + '.tar -C' + opts.unpackdir +'/')
	print("\n [>] Expanding Android Backup (TAR) to ./%s\n") % opts.unpackdir
	for line in child:
		if opts.verbose and not line.startswith("/bin/tar:"):
			# print non-informational lines
			print(" [>] Creating: ./%s/%s") % (opts.unpackdir, line),

def summary():
	child = pexpect.spawn ('tree -a -x ' + opts.unpackdir)
	print("\n [ ] Summary of extracted contents (%s):\n") % opts.unpackdir
	for line in child:
		print '\t' + line,

if __name__ == "__main__":
   main()

