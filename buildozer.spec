[app]
title = 减肥数据记录
package.name = jianfei
package.domain = org.jianfei
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
main = main.py
version = 2.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee,openssl,requests,sqlite3
android.api = 30
android.minapi = 21
android.targetapi = 30
android.ndk = 25b
android.sdk = 28
bootstraps = sdl2
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
icon.filename = data/icon.png
source.include_patterns = fonts/*.ttf
orientation = portrait
fullscreen = 0
window.resizable = 0
android.arch = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = .buildozer
bin_dir = bin
default_target = android
android.accept_sdk_license = True
