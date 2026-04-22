from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    

    datas=collect_data_files('mediapipe') + [('yolov8n.pt', '.')],
    hiddenimports=[
        'app',
        'app.ui',
        'app.ui.backend',
        'app.ui.backend.engine',
        'app.ui.backend.face_detection',
        'app.ui.backend.phone_detection',
        'app.ui.backend.eye_tracking'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # 🔥 IMPORTANT (no terminal popup)
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)