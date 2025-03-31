import os
import sys
import shutil
import PyInstaller.__main__
from pathlib import Path

def create_portable_package():
    """ポータブル版パッケージを作成"""
    # ビルドディレクトリ
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, 'dist')
    portable_dir = os.path.join(dist_dir, 'TikTokStudioMonitor-Portable')

    # 既存のディレクトリを削除
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)

    # ディレクトリを作成
    os.makedirs(portable_dir, exist_ok=True)

    # PyInstallerのオプション
    options = [
        os.path.join(root_dir, 'app', 'monitor.py'),
        '--name=TikTokStudioMonitor',
        '--onefile',
        '--noconsole',
        '--clean',
        '--distpath=' + portable_dir,

        # 必要なモジュール
        '--hidden-import=plyer',
        '--hidden-import=plyer.platforms.win',
        '--hidden-import=plyer.platforms.win.notification',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter',
        '--hidden-import=PIL._imaging',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=psutil',
        '--hidden-import=pystray',
        '--hidden-import=dotenv',
        '--hidden-import=python-dotenv',

        # データファイルの追加
        '--add-data=requirements.txt;.',

        # 追加のインポート
        '--collect-all=plyer',
        '--collect-all=pystray',
        '--collect-all=PIL',
        '--collect-submodules=plyer',
        '--collect-submodules=pystray',
    ]

    # アイコンファイルが存在する場合は追加
    icon_path = os.path.join(root_dir, 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        options.append(f'--icon={icon_path}')
        # アイコンファイルをコピー
        shutil.copy2(icon_path, portable_dir)

    # READMEファイルを作成
    create_readme(portable_dir)

    # デフォルト設定ファイルを作成
    create_default_config(portable_dir)

    # PyInstallerを実行
    PyInstaller.__main__.run(options)

    print("\nポータブルパッケージの作成が完了しました！")
    print(f"作成場所: {portable_dir}")

def create_readme(portable_dir):
    """READMEファイルを作成"""
    readme_content = """TikTok LIVE Studio Monitor - ポータブル版

使用方法：
1. TikTokStudioMonitor.exeをダブルクリックして起動
2. 初回起動時に設定画面が表示されます
3. TikTok LIVE Studioプロセスを自動検出、または手動で設定
4. 監視間隔と通知設定を調整
5. システムトレイに常駐して監視を開始

設定項目：
- プロセス名: TikTokLiveStudio.exe（自動検出可能）
- 監視間隔: デフォルト30秒
- 通知クールダウン: デフォルト300秒（5分）

注意事項：
- 設定は自動的に保存されます
- システムトレイのアイコンを右クリックで設定変更可能
- ログファイルは実行ユーザーのホームディレクトリに保存されます
"""

    with open(os.path.join(portable_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_default_config(portable_dir):
    """デフォルト設定ファイルを作成"""
    config_content = """{
    "process_name": "TikTokLiveStudio.exe",
    "check_interval": 30,
    "notification_cooldown": 300,
    "startup": false
}"""

    with open(os.path.join(portable_dir, 'default_config.json'), 'w', encoding='utf-8') as f:
        f.write(config_content)

if __name__ == "__main__":
    create_portable_package()