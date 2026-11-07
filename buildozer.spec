[app]
title = DLNA Cast
package.name = dlnacast
package.domain = org.sankarannagarajan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 1

android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE

[buildozer]
log_level = 2
warn_on_root = 1
