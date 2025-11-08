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
source.include_exts = py,png,jpg,kv,atlas,ttf

# 主程序文件
main = main.py

# 版本信息（简化版本）
version = 2.0

# 依赖包（使用较新的版本）
requirements = python3,kivy==2.3.0,kivymd==1.2.0,peewee

# Android API 配置
android.api = 33
android.minapi = 21
android.targetapi = 33

# 引导程序
bootstraps = sdl2

# Android 权限
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 应用图标路径
icon.filename = data/icon.png

# 包含字体文件
source.include_patterns = fonts/*.ttf

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# 窗口可调整大小
window.resizable = 0

# 排除测试文件和虚拟环境
source.exclude_dirs = tests, bin, venv, __pycache__

# 排除常见的无关文件
source.exclude_exts = spec, pyc, pyo, so, o, a, class, keystore

[buildozer]
# 日志级别
log_level = 2

# 构建目录
build_dir = .buildozer

# 输出目录
bin_dir = bin

# 默认目标平台
default_target = android

# 自动接受SDK许可证
android.accept_sdk_license = True
