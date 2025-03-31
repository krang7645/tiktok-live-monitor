import PyInstaller.__main__
import os
import sys

def build_exe():
    """EXEファイルをビルド"""
    # アプリケーションのルートディレクトリ
    root_dir = os.path.dirname(os.path.abspath(__file__))

    # ビルドオプション
    options = [
        os.path.join(root_dir, 'app', 'monitor.py'),  # メインスクリプト
        '--name=TikTokStudioMonitor',                 # 出力ファイル名
        '--onefile',                                  # 単一のEXEファイルに
        '--noconsole',                                # コンソール非表示
        '--clean',                                    # ビルドディレクトリをクリーン

        # 必要なモジュールを含める
        '--hidden-import=PIL._tkinter',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
    ]

    # アイコンファイルが存在する場合は追加
    icon_path = os.path.join(root_dir, 'assets', 'icon.ico')
    if os.path.exists(icon_path):
        options.append(f'--icon={icon_path}')

    # PyInstallerを実行
    PyInstaller.__main__.run(options)

    print("\nビルドが完了しました！")
    print(f"実行ファイル: {os.path.join('dist', 'TikTokStudioMonitor.exe')}")

if __name__ == "__main__":
    build_exe()
