from setuptools import setup

APP = ['calendar_app.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': "予約カレンダー登録",
        'CFBundleDisplayName': "予約カレンダー登録",
        'CFBundleIdentifier': "com.reservationcalendar",
        'CFBundleVersion': "1.0.0",
        'LSMinimumSystemVersion': "10.10",
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'google.generativeai',
        'PyQt6',
        'icalendar',
        'PIL'
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'google-generativeai',
        'PyQt6',
        'icalendar',
        'Pillow'
    ],
)