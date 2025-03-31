import os
import sys
import shutil
import PyInstaller.__main__

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
        '--distpath=' + os.path.join(portable_dir, 'app'),

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
        shutil.copy2(icon_path, portable_dir)

    # READMEファイルを作成
    create_readme(portable_dir)

    # 設定ファイルのテンプレートを作成
    create_default_config(portable_dir)

    # PyInstallerを実行
    PyInstaller.__main__.run(options)

    print("\nポータブル版パッケージの作成が完了しました！")
    print(f"パッケージの場所: {portable_dir}")

def create_readme(portable_dir):
    """READMEファイルを作成"""
    readme_content = """# TikTok LIVE Studio モニター (ポータブル版)

## 使用方法

1. このフォルダを任意の場所に配置してください
2. `app/TikTokStudioMonitor.exe` をダブルクリックで起動
3. 初回起動時に設定画面が表示されます
4. 設定完了後、システムトレイに常駐します

## 機能

- TikTok LIVE Studioの認証状態を監視
- 認証が必要になった際にデスクトップ通知を表示
- システムトレイから簡単に設定変更可能
- Windows起動時の自動起動設定可能

## 注意事項

- 設定は自動的にユーザーのホームディレクトリに保存されます
- ログファイルはユーザーのホームディレクトリに作成されます
- プログラムの終了はシステムトレイのアイコンを右クリック→「終了」から行えます

## トラブルシューティング

問題が発生した場合は、以下の手順をお試しください：

1. プログラムを一度終了し、再起動する
2. 設定を開き、プロセス名が正しいか確認する
3. TikTok LIVE Studioを再起動する

## アンインストール

1. プログラムを終了
2. このフォルダを削除
3. 必要に応じて以下のファイルを削除：
   - `%USERPROFILE%\.tiktok_monitor_config.json`
   - `%USERPROFILE%\tiktok_monitor.log`
"""

    with open(os.path.join(portable_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_default_config(portable_dir):
    """デフォルトの設定ファイルを作成"""
    default_config = {
        "process_name": "TikTokLiveStudio",
        "check_interval": 30,
        "notification_cooldown": 300,
        "autostart": False
    }

    config_dir = os.path.join(portable_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)

    with open(os.path.join(config_dir, 'default_config.json'), 'w', encoding='utf-8') as f:
        import json
        json.dump(default_config, f, indent=2)

if __name__ == "__main__":
    create_portable_package()