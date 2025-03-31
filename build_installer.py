import os
import sys
import shutil
import PyInstaller.__main__
from pathlib import Path

def create_installer_package():
    """インストーラー版パッケージを作成"""
    # ビルドディレクトリ
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, 'dist')
    installer_dir = os.path.join(dist_dir, 'TikTokStudioMonitor-Setup')

    # 既存のディレクトリを削除
    if os.path.exists(installer_dir):
        shutil.rmtree(installer_dir)

    # ディレクトリを作成
    os.makedirs(installer_dir, exist_ok=True)

    # PyInstallerのオプション
    options = [
        os.path.join(root_dir, 'app', 'monitor.py'),
        '--name=TikTokStudioMonitor',
        '--onefile',
        '--noconsole',
        '--clean',
        '--distpath=' + os.path.join(installer_dir, 'app'),

        # 必要なモジュール
        '--hidden-import=PIL._tkinter',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
    ]

    # アイコンファイルが存在する場合は追加
    icon_path = os.path.join(root_dir, 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        options.append(f'--icon={icon_path}')
        # アイコンファイルをコピー
        shutil.copy2(icon_path, installer_dir)

    # Inno Setup スクリプトを作成
    create_inno_setup_script(installer_dir)

    # PyInstallerを実行
    PyInstaller.__main__.run(options)

    print("\nインストーラーパッケージの作成準備が完了しました！")
    print("Inno Setup Compilerを使用してインストーラーを作成してください。")
    print(f"スクリプトの場所: {os.path.join(installer_dir, 'installer.iss')}")

def create_inno_setup_script(installer_dir):
    """Inno Setup スクリプトを作成"""
    script_content = f"""#define MyAppName "TikTok LIVE Studio Monitor"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name"
#define MyAppExeName "TikTokStudioMonitor.exe"

[Setup]
AppId={{{{8A7D8AE1-9F0B-4F3A-B876-6544D891A757}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
OutputDir=.
OutputBaseFilename=TikTokStudioMonitor-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\\Japanese.isl"

[Tasks]
Name: "desktopicon"; Description: "デスクトップにアイコンを作成"; GroupDescription: "アイコン:"; Flags: unchecked
Name: "startupicon"; Description: "Windows起動時に自動的に起動"; GroupDescription: "自動起動:"; Flags: unchecked

[Files]
Source: "app\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "TikTokStudioMonitor"; ValueData: "{{app}}\\{{#MyAppExeName}}"; Flags: uninsdeletevalue; Tasks: startupicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
"""

    with open(os.path.join(installer_dir, 'installer.iss'), 'w', encoding='utf-8') as f:
        f.write(script_content)

if __name__ == "__main__":
    create_installer_package()