ini
[app]
title = DLNA Cast
package.name = dlnacast
package.domain = org.sankarannagarajan
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,upnpclient,requests
orientation = portrait
fullscreen = 1

# Android specific configurations
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a

# Critical Network Permissions for DLNA Casting
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, CHANGE_WIFI_MULTICAST_STATE

[buildozer]
log_level = 2
warn_on_root = 1
#   Then, invoke the command line with the "demo" profile:
#
#        buildozer --profile demo android debug
#
#   Environment variable overrides have priority over profile overrides.
