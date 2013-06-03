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
	version = "v1.0 - @ChrisJohnRiley"
	logo(version)

	parser = optparse.OptionParser(usage=usage, version=version)

	parser.add_option("-d", "--directory", dest="directory", help="Directory containing apps folder for repacking")
	parser.add_option("-b", "--backfile", dest="backfile", help="Resulting Android Backup filename")
	parser.add_option("-l", "--list", dest="list", help="List created from original backup")
	parser.add_option("-o", "--original", dest="original", help="Original Android Backup filename")
	parser.add_option("-r", "--restore", dest="restore", help="Restore to device on completion", action="store_true")

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

	adbrestore = setup(opts.backfile)
	checks(opts.backfile, opts.directory)

	# take list from user supplied file or recreate from original ab
	if opts.list:
		listfile = opts.list	
	else:
		randfilename = decode(opts.original)
		listfile = create_list(opts.original, randfilename)

	pack(opts.directory, opts.backfile, listfile, opts.original)

	if opts.restore:
		restore(adbrestore)

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

def setup(backfile):
	
	# setup variables for the script
	adbrestore = 'adb restore ' + backfile

	return (adbrestore)

def checks(backfile, directory):

	# check if file and/or directory exist already
	if os.path.exists(backfile):
		print(" [X] Restore file of the same name: %s already exists") % backfile
		sys.exit(1)

	if not os.path.exists(directory):
		print(" [X] Source directory: %s does not exist") % directory
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

def restore(adbrestore):

	# restore application over adb
	print(" [ ] Running Android Restore: %s") % adbrestore

	print("\n [>] Accept restore prompt on Android device to complete restore process...")
	child = pexpect.spawn (adbrestore)
	for line in child:
		print line,

def decode(original):

	# decode Android Backup using dd and openssl zlib
	print(" [ ] Unpacking original Android Backup (%s) to create list") % original

	randfilename = ''.join(random.choice(string.lowercase) for i in range(6))
	# convert ab to tar
	child = pexpect.spawn ('/bin/bash -c "dd if=' + original + ' bs=24 skip=1 | openssl zlib -d > ' + randfilename + '.tar"')
	i = child.expect('records out')

	if i==1:
		print(" [X] Unable to decompress original Android Backup file (%s)") % original
		sys.exit(1)

	if not os.path.exists(randfilename + '.tar'):
		print(" [X] Unable to create TAR file (%s)") % (randfilename + '.tar')
		sys.exit(1)

	return randfilename

def create_list(original, randfilename):

	# create list from TAR file (for use in repacking)
	print(" [ ] Creating filelist from TAR file")
	child = pexpect.spawn ('/bin/bash -c "tar -tf ' + randfilename + '.tar > ' + original + '.list"')
	for line in child:	
		print line,
	listfile = original + '.list'

	# cleanup temp file
	os.remove(randfilename + '.tar')

	return listfile

def pack(directory, backfile, listfile, original):

	# create tar from source directory
	randfilename = ''.join(random.choice(string.lowercase) for i in range(6))
	print("\n [>] Creating TAR file from source directory ./%s\n") % directory
	child = pexpect.spawn ('star -c -v -f ./' + randfilename + '.tar -no-dirslash list=' + listfile + ' -C ' + directory)
	for line in child:
		if line.startswith('a '):	
			print(" [] Added: %s") % ('./' + directory + '/' + line[2:]),

	print("\n [>] Creating Android Backup from source directory")
	child = pexpect.spawn ('/bin/bash -c "dd if=' + original + ' bs=24 count=1 of=' + backfile + '; openssl zlib -in ' + randfilename + '.tar >> ' + backfile + '"')
	i = child.expect('records out')

	if i==1:
		print(" [X] Unable to compress Android Backup file (%s)") % backfile
		sys.exit(1)

	# cleanup temp file
	os.remove(randfilename + '.tar')

if __name__ == "__main__":
   main()

