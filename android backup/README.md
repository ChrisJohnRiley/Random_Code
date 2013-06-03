Android Backup (unpacker / Packer)
==================================

Example:

./ab_unpacker -p com.app.android -b app.ab

- Creates an adb backup of com.app.android called app.ab and uncompresses it into ./com.app.android

./ab_packer -d ./com.app.android -b app_edit.ab -o app.ab -r

- Repacks the contents of ./com.app.android into app_new.ab and attempts to restore it via adb