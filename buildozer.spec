[app]
title = AI TRADING BOT ULTIMATE
package.name = aitradingbotultimate
package.domain = com.hassanstudio.aitrading
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 2.0.0

requirements = python3,flet==0.24.1,websockets==12.0,aiohttp==3.9.5,certifi,idna,charset-normalizer,urllib3

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,WAKE_LOCK
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
