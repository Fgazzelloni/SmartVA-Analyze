# -*- mode: python -*-
a = Analysis(['src/vaUI.py'],
             pathex=['/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='SmartVA',
          debug=False,
          strip=None,
          upx=False,
          console=False , icon='pkg/icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               [('res/logo.png', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/res/logo.png', 'DATA')],
               [('res/help.html', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/res/help.html', 'DATA')],
               [('tariffs-adult.csv', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/tariffs-adult.csv', 'DATA')],
               [('tariffs-child.csv', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/tariffs-child.csv', 'DATA')],
               [('tariffs-neonate.csv', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/tariffs-neonate.csv', 'DATA')],
               [('validated-adult.csv', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/validated-adult.csv', 'DATA')],
               [('validated-child.csv', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/validated-child.csv', 'DATA')],
               [('validated-neonate.csv', '/Volumes/Aequitas/Users/yanokwa/Documents/Work/Nafundi/Projects/IHME/ihme-va/src/validated-neonate.csv', 'DATA')],
               strip=None,
               upx=False,
               name='SmartVA')
app = BUNDLE(coll,
             name='SmartVA.app',
             icon='pkg/icon.icns')
