#!/usr/bin/python
# -*- coding:utf8 -*-


# 
# ab_packer.py (Android Backup re-packer)
#
# Repacks an unpacked Android Backup for restoration
#

import pexpect
import optparse
import random
import sys
import os
import string

def main():

	usage = "\n%prog [options] arguments"
	version = "v1.1 - @ChrisJohnRiley"
	logo(version)

	parser = optparse.OptionParser(usage=usage, version=version)

	parser.add_option("-d", "--directory", dest="directory", help="Directory containing apps folder for repacking")
	parser.add_option("-b", "--backfile", dest="backfile", help="Resulting Android Backup filename (NEW)")
	parser.add_option("-l", "--list", dest="list", help="List created from original backup")
	parser.add_option("-o", "--original", dest="original", help="Original Android Backup filename")
	parser.add_option("-r", "--restore", dest="restore", help="Restore to device on completion", action="store_true")
	parser.add_option("-v", "--verbose", dest="verbose", help="Verbose output", action="store_true")
	parser.add_option("-x", "--overwrite", dest="overwrite", help="Overwrite files/directories", action="store_true")

	global opts
	(opts, args) = parser.parse_args()

	if opts.directory and opts.backfile:
		if not opts.original:
			print("\n [X] Original Android Backup file required\n")
			parser.print_help()
			print("\n")
			sys.exit(0)
		else:
			print("\n [ ] Starting script to create %s from ./%s") % (opts.backfile, opts.directory)
	else:
		print("\n [X] Required arguements [directory], [backfile], and [original] not provided\n")
		parser.print_help()
		print("\n")
		sys.exit(0)

	if opts.overwrite:
		print("\n [!] Overwriting enabled -\n")
		print("\t - existing backup data will be overwritten")
		print("\t - existing files within the unpack directory will be overwritten\n")

	setup()
	checks()

	# take list from user supplied file or recreate from original ab
	if opts.list:
		opts.listfile = opts.list
	else:
		decode()
		create_list()

	pack()

	if opts.verbose:
		# output summary of packed files
		summary()
	if opts.restore:
		restore()

	print("\n [ ] Script completed...\n\n")

def logo(version):
	print('''
       _                         _             
      | |                       | |            
  __ _| |__     _ __   __ _  ___| | _____ _ __ 
 / _` | '_ \   | '_ \ / _` |/ __| |/ / _ \ '__|
| (_| | |_) |  | |_) | (_| | (__|   <  __/ |   
 \__,_|_.__/   | .__/ \__,_|\___|_|\_\___|_|   
         ______| |                             
        |_\__\_|_|       %s''') % version

def setup():
	
	# setup variables for the script
	opts.adbrestore = 'adb restore ' + opts.backfile

def checks():

	if not opts.overwrite:

		# check if file and/or directory exist already
		if os.path.exists(opts.backfile):
			print(" [X] Restore file of the same name: %s already exists\n") % opts.backfile
			sys.exit(1)
	
		if not os.path.exists(opts.directory):
			print(" [X] Source directory: %s does not exist\n") % opts.directory
			sys.exit(1)

	# check openssl zlib support
	child = pexpect.spawn ('openssl -help')
	i = child.expect ('zlib')

	if i==1:
		print(" [X] Openssl Version does not support zlib")
		sys.exit(1)

	# check for star
	child = pexpect.spawn ('star --version')
	i = child.expect ('[Oo]ptions')

	if i==1:
		print(" [X] Star does not appear to be installed")
		print(" [X] The star commandline tool is needed as tar does not support removal of trailing slashes")
		print(" [X] Please install star and try again")
		sys.exit(1)

def restore():

	# restore application over adb
	print(" [ ] Running Android Restore: %s") % opts.adbrestore

	print("\n [>] Accept restore prompt on Android device to complete restore process...\n")
	child = pexpect.spawn (opts.adbrestore)
	# check if adb errored out - can't use expect due to stderr?
	for line in child:
		if "unable to connect for backup" in line:
			print(" [X] ADB is unable to detect an Android device - cancelling restore\n")
			sys.exit(1)
		else:
			print line,

def decode():

	# decode Android Backup using dd and openssl zlib
	print(" [ ] Unpacking original Android Backup (%s) to create list") % opts.original

	opts.randfilename = ''.join(random.choice(string.lowercase) for i in range(6))
	# convert ab to tar
	child = pexpect.spawn ('/bin/bash -c "dd if=' + opts.original + ' bs=24 skip=1 | openssl zlib -d > ' + opts.randfilename + '.tar"')
	i = child.expect('records out')

	if i==1:
		print(" [X] Unable to decompress original Android Backup file (%s)") % opts.original
		sys.exit(1)

	if not os.path.exists(opts.randfilename + '.tar'):
		print(" [X] Unable to create TAR file (%s)") % (opts.randfilename + '.tar')
		sys.exit(1)

def create_list():

	# create list from TAR file (for use in repacking)
	print(" [ ] Creating filelist from TAR file (%s)") % (opts.original + '.tar.list')
	child = pexpect.spawn ('/bin/bash -c "tar -tf ' + opts.randfilename + '.tar > ' + opts.original + '.tar.list"')
	for line in child:	
		print line,
	opts.listfile = opts.original + '.tar.list'

	# cleanup temp file
	os.remove(opts.randfilename + '.tar')

def pack():

	# create tar from source directory
	opts.randfilename = ''.join(random.choice(string.lowercase) for i in range(6))
	print("\n [>] Creating TAR file from source directory ./%s\n") % opts.directory
	child = pexpect.spawn ('star -c -v -f ./' + opts.randfilename + '.tar -no-dirslash list=' + opts.listfile + ' -C ' + opts.directory)
	for line in child:
		if line.startswith('a '):	
			print(" [] Added: %s") % ('./' + opts.directory + '/' + line[2:]),

	print("\n [>] Creating Android Backup from source directory")
	child = pexpect.spawn ('/bin/bash -c "dd if=' + opts.original + ' bs=24 count=1 of=' + opts.backfile + '; openssl zlib -in ' + opts.randfilename + '.tar >> ' + opts.backfile + '"')
	i = child.expect('records out')

	if i==1:
		print(" [X] Unable to compress Android Backup file (%s)") % opts.backfile
		sys.exit(1)
	else:
		print(" [ ] Android Backup file (%s) created") % opts.backfile

	# cleanup temp file
	os.remove(opts.randfilename + '.tar')

def summary():
	child = pexpect.spawn ('tree -a -x ' + opts.directory)
	print("\n [ ] Summary of packed contents (%s):\n") % opts.directory
	for line in child:
		print '\t' + line,

if __name__ == "__main__":
   main()
