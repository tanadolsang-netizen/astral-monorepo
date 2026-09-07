@echo off
set ANDROID_HOME=D:\AI\android-sdk
set JAVA_HOME=%ANDROID_HOME%\jdk-17
set GRADLE_HOME=%ANDROID_HOME%\gradle
set PATH=%GRADLE_HOME%\bin;%JAVA_HOME%\bin;%ANDROID_HOME%\cmdline-tools\latest\bin;%ANDROID_HOME%\platform-tools;%PATH%
cd /d D:\AI\astral-expo
echo Starting Android build...
npx expo run:android
pause
