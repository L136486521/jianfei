[app]
title = 减肥数据记录
package.name = jianfei
package.domain = org.jianfei

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 2.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee==3.14.4,android,sqlite3

orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1

presplash.filename = data/presplash.png
icon.filename = data/icon.png

fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

copyright = Copyright © 2023 减肥数据记录

android.api = 31
android.minapi = 21
android.sdk = 21
android.ndk = 25b
android.ndk_api = 21

android.accept_sdk_license = True

android.arch = arm64-v8a

p4a.branch = develop

# 包含数据文件
source.include_patterns = fonts/*.ttf

# 入口点
entrypoint = main.py

buildozer.build_dir = bin

buildozer.log_level = 2
