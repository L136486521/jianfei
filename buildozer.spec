[app]
title = 减肥数据记录
package.name = jianfei
package.domain = org.jianfei

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

version = 2.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee

orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1

[app]
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

[buildozer]
android.accept_sdk_license = True

[app]
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[app]
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 28

[app]
android.arch = arm64-v8a

[app]
p4a.branch = develop

[app]
# 包含字体文件
source.include_exts = py,png,jpg,kv,atlas,ttf

[app]
# 包含数据文件
source.include_patterns = fonts/*.ttf

[app]
# 入口点
entrypoint = main.py
