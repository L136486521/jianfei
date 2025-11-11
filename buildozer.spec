[app]
title = 减肥数据记录
package.name = jianfei
package.domain = org.jianfei

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json,txt

version = 2.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee==3.14.4,android

orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1

# 确保图标文件存在且路径正确
presplash.filename = data/presplash.png
icon.filename = data/icon.png

fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

copyright = Copyright © 2023 减肥数据记录

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21

android.accept_sdk_license = True
android.arch = arm64-v8a

p4a.branch = develop

# 包含数据文件和字体文件
source.include_patterns = fonts/*.ttf,data/*.png,data/*.jpg

# 入口点
entrypoint = main.py

buildozer.build_dir = bin
buildozer.log_level = 2

# 添加应用名称（显示在桌面）
app_name = 减肥数据记录

# 添加版本信息
version.regex = __version__ = '(.*)'
version.filename = %(source.dir)s/main.py

# 确保包含所有资源
source.include_exts = py,png,jpg,kv,atlas,ttf,db,json,txt,xml

# 添加这些配置来避免常见问题
android.skip_update = False
android.gradle_download = True

# 设置更兼容的构建工具版本
android.build_tools_version = 30.0.3
