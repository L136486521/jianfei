[app]
title = 减肥数据记录
package.name = jianfei
package.domain = org.jianfei

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,db

version = 2.0
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee==3.14.4,android

orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1

presplash.filename = data/presplash.png
icon.filename = data/icon.png

fullscreen = 0
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

copyright = Copyright © 2023 减肥数据记录

# 更新 Android 配置
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 23b
android.ndk_api = 21

# 启用自动接受许可证
android.accept_sdk_license = True

android.arch = arm64-v8a

# 使用稳定分支
p4a.branch = master

# 包含数据文件
source.include_patterns = fonts/*.ttf,data/*.png

# 入口点
entrypoint = main.py

# 构建配置
buildozer.build_dir = bin
buildozer.log_level = 2

# 添加这些配置来避免常见问题
android.skip_update = False
android.gradle_download = True

# 添加这些以处理依赖关系
android.gradle_dependencies = 
android.aars = 

# 设置更兼容的构建工具版本
android.build_tools_version = 30.0.3
