[app]
# 应用标题
title = 减肥数据记录

# 应用包名
package.name = jianfei

# 应用域名
package.domain = org.jianfei

# 源文件目录
source.dir = .

# 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,ttf,db

# 主程序文件
main = main.py

# 版本信息
version = 2.0

# 版本号匹配规则
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# 依赖包
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee,openssl,requests,sqlite3

# Android API 配置
android.api = 30
android.minapi = 21
android.targetapi = 30

# 引导程序
bootstraps = sdl2

# Android 权限
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 应用图标路径（使用您现有的图标）
icon.filename = %(source.dir)s/data/icon.png

# 日志级别
log_level = 2

# 包含字体文件
source.include_patterns = fonts/*.ttf

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# 窗口可调整大小
window.resizable = 0

# 包含数据文件
include.data = fonts/simkai.ttf

# 排除测试文件和虚拟环境
source.exclude_dirs = tests, bin, venv, __pycache__

# 排除常见的无关文件
source.exclude_exts = spec, pyc, pyo, so, o, a, db, class, keystore

# 应用配置结束

[buildozer]
# 日志级别
log_level = 2

# 警告设置
warn_on_root = 1

# 构建目录
build_dir = .buildozer

# 输出目录
bin_dir = bin

# 默认目标平台
default_target = android

# 自动接受SDK许可证
android.accept_sdk_license = True

# 构建配置结束