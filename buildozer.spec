[app]
# 应用标题
title = 减肥数据记录
# 应用包名
package.name = jianfei
# 应用域名
package.domain = org.jianfei

# 源文件目录
source.dir = .
# 主程序文件
source.include_exts = py,png,jpg,kv,atlas,ttf
# 入口文件
main = main.py

# 版本信息
version = 2.0
# 版本号（必须为整数）
version.regex = __version__ = ['"](.*)['"]
version.filename = %(source.dir)s/main.py

# 需求配置
requirements = python3,kivy,kivymd,peewee,openssl,requests

# 支持的 Android API 级别
android.api = 30
# 最小 Android 版本
android.minapi = 21
# 目标 Android 版本
android.targetapi = 30

# 引导程序
bootstraps = sdl2

# 权限设置
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 应用图标（需要准备不同尺寸的图标）
icon.filename = %(source.dir)s/data/icon.png

# 预设配置
preset.filename = %(source.dir)s/buildozer_preset.py

# 日志级别
log_level = 2

# 中文字体支持
source.include_patterns = fonts/*.ttf

[buildozer]
# 日志级别
log_level = 2
# 创建调试版本

warn_on_root = 1
