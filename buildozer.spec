[app]

title = AutoClicker
package.name = autoclicker
package.domain = org.elkeyvers
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt,log
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.allow_backup = True
android.debug_obfuscate = False
android.debug_obfuscate_level = 0

# Чтобы логи и конфиги сохранялись
android.extra_permissions = android.permission.MANAGE_EXTERNAL_STORAGE

# Иконка (можешь заменить)
icon.filename = %(source.dir)s/icon.png

# Чтобы Kivy работал быстрее
android.enable_androidx = True
android.gradle_dependencies = androidx.appcompat:appcompat:1.4.1

# Ускорение рендера
android.opengl_es_version = 2

# Чтобы приложение могло писать файлы
presplash.filename = %(source.dir)s/presplash.png

# Отключаем ненужные сервисы
android.disable_androidx_library_check = True

# Включаем многопоточность
android.allow_cleartext_traffic = True

# Логи Kivy
log_level = 2


[buildozer]

log_level = 2
warn_on_root = 0
