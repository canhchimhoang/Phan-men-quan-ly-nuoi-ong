#!/usr/bin/env python3
"""Chuẩn bị thư mục android/ để ứng dụng chạy được thông báo nhắc lịch.

Chạy từ thư mục gốc dự án:   python3 tools/patch_android.py
- Nếu chưa có android/ (hoặc ios/) thì gọi `flutter create` để sinh ra.
- Thêm quyền thông báo / báo thức và các receiver của flutter_local_notifications.
- Bật core library desugaring (bắt buộc với flutter_local_notifications).
- Đặt tên hiển thị của ứng dụng.
Có thể chạy lại nhiều lần (idempotent).
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

APP_LABEL = "Quản lý nuôi ong"
MANIFEST = "android/app/src/main/AndroidManifest.xml"

PERMISSIONS = [
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.VIBRATE",
    "android.permission.SCHEDULE_EXACT_ALARM",
    "android.permission.USE_EXACT_ALARM",
]

RECEIVERS = """
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ActionBroadcastReceiver" />
        <receiver android:exported="false" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
        <receiver android:exported="false" android:enabled="true" android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
            </intent-filter>
        </receiver>
"""


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def ensure_platforms():
    if os.path.isdir("android") and os.path.isdir("ios"):
        return
    flutter = shutil.which("flutter")
    if not flutter:
        sys.exit("Không tìm thấy lệnh 'flutter'. Hãy cài Flutter SDK trước.")
    print(">> flutter create (sinh thư mục android/ và ios/)")
    subprocess.check_call([
        flutter, "create", ".", "--platforms=android,ios",
        "--project-name", "quan_ly_nuoi_ong", "--org", "vn.nuoiong",
    ])
    # flutter create sinh test mẫu tham chiếu MyApp -> bỏ đi cho khỏi lỗi analyze
    t = "test/widget_test.dart"
    if os.path.exists(t) and "MyApp" in read(t):
        os.remove(t)


def patch_manifest():
    s = read(MANIFEST)
    # 1) quyền
    add = ""
    for perm in PERMISSIONS:
        if perm not in s:
            add += f'    <uses-permission android:name="{perm}"/>\n'
    if add:
        s = re.sub(r"(<manifest[^>]*>\n?)", lambda m: m.group(1) + add, s, count=1)
    # 2) receiver
    if "ScheduledNotificationReceiver" not in s:
        s = s.replace("</application>", RECEIVERS + "    </application>", 1)
    # 3) tên ứng dụng
    s = re.sub(r'(<application[^>]*?android:label=")[^"]*(")',
               lambda m: m.group(1) + APP_LABEL + m.group(2), s, count=1, flags=re.S)
    write(MANIFEST, s)
    print(">> đã cập nhật AndroidManifest.xml")


def patch_gradle():
    for name, kts in (("android/app/build.gradle.kts", True), ("android/app/build.gradle", False)):
        if not os.path.exists(name):
            continue
        s = read(name)
        if "desugar_jdk_libs" in s:
            print(f">> {name} đã có desugaring")
            return
        if kts:
            enable = "        isCoreLibraryDesugaringEnabled = true\n"
            dep = '    coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")\n'
        else:
            enable = "        coreLibraryDesugaringEnabled true\n"
            dep = "    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:2.1.4'\n"
        if "compileOptions {" not in s:
            sys.exit(f"Không tìm thấy compileOptions trong {name}")
        s = s.replace("compileOptions {\n", "compileOptions {\n" + enable, 1)
        if re.search(r"^dependencies\s*\{", s, re.M):
            s = re.sub(r"^(dependencies\s*\{\n)", lambda m: m.group(1) + dep, s, count=1, flags=re.M)
        else:
            s += "\ndependencies {\n" + dep + "}\n"
        write(name, s)
        print(f">> đã bật desugaring trong {name}")
        return
    sys.exit("Không tìm thấy android/app/build.gradle(.kts)")


if __name__ == "__main__":
    ensure_platforms()
    patch_manifest()
    patch_gradle()
    print("Xong. Tiếp theo: flutter pub get && flutter build apk --release")
