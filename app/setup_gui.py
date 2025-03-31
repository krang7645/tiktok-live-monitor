import tkinter as tk
from tkinter import ttk, messagebox
import os
import json
import psutil
from typing import Optional, Dict

class SetupDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TikTok Studio Monitor セットアップ")
        self.root.geometry("500x400")

        # 設定を保存するパス
        self.config_path = os.path.join(os.path.expanduser('~'), '.tiktok_monitor_config.json')

        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        """ウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # プロセス名設定
        ttk.Label(main_frame, text="監視するプロセス名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.process_name_var = tk.StringVar(value="TikTokLiveStudio")
        self.process_name_entry = ttk.Entry(main_frame, textvariable=self.process_name_var, width=40)
        self.process_name_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="検索", command=self.search_process).grid(row=0, column=2, padx=5)

        # チェック間隔設定
        ttk.Label(main_frame, text="チェック間隔（秒）:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.check_interval_var = tk.StringVar(value="30")
        ttk.Entry(main_frame, textvariable=self.check_interval_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)

        # 通知クールダウン設定
        ttk.Label(main_frame, text="通知クールダウン（秒）:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cooldown_var = tk.StringVar(value="300")
        ttk.Entry(main_frame, textvariable=self.cooldown_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)

        # 自動起動設定
        self.autostart_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="Windowsスタートアップに登録",
                       variable=self.autostart_var).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # 説明テキスト
        ttk.Label(main_frame, text="設定について:", font=("", 10, "bold")).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(20,5))
        help_text = """
• プロセス名: TikTok LIVE Studioの実行ファイル名です。「検索」ボタンで自動検出できます。
• チェック間隔: プロセスの状態を確認する間隔（秒）
• 通知クールダウン: 通知の最小間隔（秒）
• 自動起動: Windowsの起動時に自動的に監視を開始します
        """
        ttk.Label(main_frame, text=help_text, wraplength=450, justify=tk.LEFT).grid(
            row=5, column=0, columnspan=3, sticky=tk.W, pady=5)

        # 保存ボタン
        ttk.Button(main_frame, text="設定を保存", command=self.save_config).grid(
            row=6, column=0, columnspan=3, pady=20)

    def search_process(self):
        """実行中のTikTokプロセスを検索"""
        tiktok_processes = []
        for proc in psutil.process_iter(['name']):
            try:
                if 'tiktok' in proc.info['name'].lower():
                    tiktok_processes.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if tiktok_processes:
            if len(tiktok_processes) == 1:
                self.process_name_var.set(tiktok_processes[0])
                messagebox.showinfo("検出成功", f"TikTokプロセスを検出しました: {tiktok_processes[0]}")
            else:
                self.show_process_selection(tiktok_processes)
        else:
            messagebox.showwarning("検出失敗",
                "TikTok関連のプロセスが見つかりませんでした。\n"
                "TikTok LIVE Studioを起動してから再試行してください。")

    def show_process_selection(self, processes):
        """複数のプロセスが見つかった場合の選択ダイアログ"""
        select_window = tk.Toplevel(self.root)
        select_window.title("プロセスの選択")
        select_window.geometry("300x200")

        ttk.Label(select_window, text="監視するプロセスを選択してください:").pack(pady=10)

        listbox = tk.Listbox(select_window, width=40)
        for proc in processes:
            listbox.insert(tk.END, proc)
        listbox.pack(pady=5)

        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_process = listbox.get(selection[0])
                self.process_name_var.set(selected_process)
                select_window.destroy()

        ttk.Button(select_window, text="選択", command=on_select).pack(pady=10)

    def create_startup_shortcut(self):
        """Windowsスタートアップにショートカットを作成"""
        try:
            import winreg
            import sys

            # 実行ファイルのパス
            exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

            # レジストリキーを開く
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                               winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)

            # 値を設定
            winreg.SetValueEx(key, "TikTokStudioMonitor", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
            return True
        except Exception as e:
            messagebox.showerror("エラー", f"スタートアップ登録に失敗しました: {e}")
            return False

    def remove_startup_shortcut(self):
        """Windowsスタートアップからショートカットを削除"""
        try:
            import winreg

            # レジストリキーを開く
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                               winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)

            # 値を削除
            winreg.DeleteValue(key, "TikTokStudioMonitor")
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def save_config(self):
        """設定を保存"""
        try:
            config = {
                'process_name': self.process_name_var.get(),
                'check_interval': int(self.check_interval_var.get()),
                'notification_cooldown': int(self.cooldown_var.get()),
                'autostart': self.autostart_var.get()
            }

            # 設定の検証
            if not config['process_name']:
                raise ValueError("プロセス名を入力してください")
            if config['check_interval'] < 1:
                raise ValueError("チェック間隔は1秒以上に設定してください")
            if config['notification_cooldown'] < 1:
                raise ValueError("通知クールダウンは1秒以上に設定してください")

            # 自動起動の設定
            if config['autostart']:
                self.create_startup_shortcut()
            else:
                self.remove_startup_shortcut()

            # 設定をファイルに保存
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            messagebox.showinfo("成功", "設定を保存しました")
            self.root.destroy()

        except ValueError as e:
            messagebox.showerror("エラー", str(e))
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました: {e}")

    def load_config(self):
        """保存された設定を読み込む"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                self.process_name_var.set(config.get('process_name', 'TikTokLiveStudio'))
                self.check_interval_var.set(str(config.get('check_interval', 30)))
                self.cooldown_var.set(str(config.get('notification_cooldown', 300)))
                self.autostart_var.set(config.get('autostart', False))
        except Exception:
            pass  # 設定ファイルの読み込みに失敗した場合はデフォルト値を使用

    def run(self) -> Optional[Dict]:
        """設定ダイアログを実行"""
        self.root.mainloop()

        # 設定ファイルから最終的な設定を読み込んで返す
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None