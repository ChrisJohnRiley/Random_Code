Android Backup (unpacker / packer)
==================================

requires:

- openssl with zlib support
- star (apt-get install star)


Simple Python scripts to perform:

- an adb backup of a specific application and uncompress it to a directory structure
- recompress a directory structure back into a valid adb restore file


Example:

./ab_unpacker.py -p com.app.android -b app.ab

- Creates an adb backup of com.app.android called app.ab and uncompresses it into ./com.app.android

./ab_packer.py -d ./com.app.android -b app_edit.ab -o app.ab -r

- Repacks the contents of ./com.app.android into app_new.ab and attempts to restore it via adb