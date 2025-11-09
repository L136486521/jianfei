[app]

# (str) Title of your application
title = 减肥数据记录

# (str) Package name
package.name = jianfei

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,db

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
requirements = python3,kivy==2.1.0,kivymd==1.1.1,peewee==3.14.4,sqlite3

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# (str) App copyright info
copyright = Copyright © 2023 减肥数据记录

# (str) App description
#description = 

# (str) Android logcat filters (by default use logcat level method: *:S myapp:D)
#logcat_filters = *:S python:D

# (bool) Copy the splash screen from source to build (default True)
#copy_splash = True

# (bool) Copy the icon from source to build (default True)
#copy_icon = True

#
# Android specific
#

# (bool) Indicates if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 21

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (str) Android material theme
#android.material_theme = 

# (str) Android manifest placeholders
#android.manifest_placeholders = 

# (list) Placeholders keys to inject in the AndroidManifest.xml file.
# The format is a list of key=value pairs, e.g.
# android.manifest_placeholders = ["myAppId"="123456789", "myAppName"="My App Name"]
# This will replace the corresponding variables in the manifest file.

# (str) Android additional manifest xml, the root tag should be 'manifest'
#android.extra_manifest_xml = 

# (str) Android additional manifest application xml, the root tag should be 'application'
#android.extra_manifest_application_xml = 

# (str) Android additional manifest activity xml, the root tag should be 'activity'
#android.extra_manifest_activity_xml = 

# (str) Android additional manifest service xml, the root tag should be 'service'
#android.extra_manifest_service_xml = 

# (str) Android additional manifest receiver xml, the root tag should be 'receiver'
#android.extra_manifest_receiver_xml = 

# (str) Android additional manifest provider xml, the root tag should be 'provider'
#android.extra_manifest_provider_xml = 

#
# Python for android (p4a) specific
#

# (str) python-for-android URL to use for checkout
#p4a.url =

# (str) python-for-android fork to use in case if p4a.url is not specified, defaults to upstream (kivy)
#p4a.fork =

# (str) python-for-android branch to use, defaults to master
#p4a.branch =

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
#p4a.port =

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
#ios.kivy_ios_url = https://github.com/kivy/kivy-ios
#ios.kivy_ios_branch = master

# Another platform dependency: ios-deploy
# Uncomment to use a custom checkout
#ios.ios_deploy_dir = ../ios_deploy
# Or specify URL and branch
#ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
#ios.ios_deploy_branch = 1.10.0

# (bool) Whether to copy the splash screen & icon or not (default True)
#ios.copy_splash = True
#ios.copy_icon = True

# (str) Path to the icon and splash files (should be in the same folder and named icon.png and splash.png)
#ios.icon_name = icon.png
#ios.splash_name = splash.png

# (str) Bundle name (default is the same as title)
#ios.bundle_name = 

# (str) Xcode project configuration type (default is Release)
#ios.configuration = Release

# (str) Xcode project scheme to use (default is the same as bundle_name)
#ios.scheme = 

# (int) Xcode project version
#ios.xcode_version = 

# (str) iOS development team ID
#ios.development_team = 

# (str) Minimum iOS version to support
#ios.minimum_version = 9.0

# (str) The directory in which your project's .xcodeproj is located
#ios.xcodeproj_dir = 

#
# Buildozer specific
#

# (str) Directory where to store the builds
buildozer.build_dir = bin

# (str) Directory in the build directory where the logs are stored
#buildozer.log_dir = bin/logs

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
buildozer.log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
#buildozer.disable_root_check = 0

# (str) Path to build artifact storage, absolute or relative to spec file
# buildozer.bin_dir = bin

# (str) Path to build output (apk or ipa) storage, absolute or relative to spec file
# buildozer.bin_dir = bin

# (str) Folders to be added to the classpath (Java only)
#buildozer.classpath =

# (str) Folders to be added to the javac classpath (Java only)
#buildozer.javac_classpath =

# (dict) Java options (Java only)
# buildozer.java_opts = {}

# (list) List of build options to use
# For example, to ignore a certain requirement during the build:
#buildozer.build_options = ["--ignore-requirements=python3,kivy"]

# (str) Allow the use of the requirements from the system. (Default 0)
#buildozer.allow_system_requirements = 0

# (str) Run the build with this number of parallel jobs (Default 1)
#buildozer.jobs = 1

# (bool) Clean the build before running the build command (Default True)
#buildozer.clean_before_build = True

# (bool) Clean the build after running the build command (Default False)
#buildozer.clean_after_build = False

# (bool) Run the build in verbose mode (Default False)
#buildozer.verbose = False

# (bool) Run the build in debug mode (Default False)
#buildozer.debug = False

# (bool) Run the build in profile mode (Default False)
#buildozer.profile = False

# (bool) Run the build in optimize mode (Default False)
#buildozer.optimize = False

# (str) Path to the build configuration file
#buildozer.config_file = 

# (str) Path to the build log file
#buildozer.log_file = 

# (str) Path to the build error log file
#buildozer.error_log_file = 

# (str) Path to the build warning log file
#buildozer.warning_log_file = 

# (str) Path to the build info log file
#buildozer.info_log_file = 

# (str) Path to the build debug log file
#buildozer.debug_log_file = 

# (bool) Enable colors in the build output (Default True)
#buildozer.colors = True

# (bool) Disable the update check (Default False)
#buildozer.disable_update_check = False

# (bool) Allow the buildozer to run as root (Default False)
#buildozer.allow_root = False
