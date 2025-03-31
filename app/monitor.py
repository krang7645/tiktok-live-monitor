import os
import sys
import time
import psutil
import logging
from datetime import datetime
from plyer import notification
import pystray
from PIL import Image
import threading
import json
from setup_gui import SetupDialog

class SimpleMonitor:
    def __init__(self, config=None):
        self.config = config or {}
        self.process_name = self.config.get('process_name', 'TikTokLiveStudio')
        self.check_interval = self.config.get('check_interval', 30)
        self.notification_cooldown = self.config.get('notification_cooldown', 300)
        self.last_notification_time = None
        self.running = True
        self.setup_tray()

    def setup_tray(self):
        """システムトレイアイコンのセットアップ"""
        # デフォルトの画像を作成（黒い16x16のイメージ）
        image = Image.new('RGB', (16, 16), 'black')
        menu = pystray.Menu(
            pystray.MenuItem("設定", self.show_settings),
            pystray.MenuItem("終了", self.stop_monitoring)
        )
        self.icon = pystray.Icon(
            "TikTokMonitor",
            image,
            "TikTok Studio Monitor",
            menu=menu
        )

    def show_settings(self):
        """設定ダイアログを表示"""
        def show_dialog():
            dialog = SetupDialog()
            new_config = dialog.run()
            if new_config:
                self.update_config(new_config)

        # 設定ダイアログを別スレッドで表示
        settings_thread = threading.Thread(target=show_dialog)
        settings_thread.start()

    def update_config(self, new_config):
        """設定を更新"""
        self.config = new_config
        self.process_name = new_config.get('process_name', self.process_name)
        self.check_interval = new_config.get('check_interval', self.check_interval)
        self.notification_cooldown = new_config.get('notification_cooldown', self.notification_cooldown)
        logging.info("設定を更新しました")

    def should_notify(self):
        """通知クールダウンチェック"""
        if self.last_notification_time is None:
            return True

        time_diff = (datetime.now() - self.last_notification_time).total_seconds()
        return time_diff > self.notification_cooldown

    def send_notification(self, title, message):
        """デスクトップ通知を送信"""
        if not self.should_notify():
            return

        try:
            notification.notify(
                title=title,
                message=message,
                app_icon=None,
                timeout=10
            )
            self.last_notification_time = datetime.now()
            logging.info(f"通知を送信しました: {title}")
        except Exception as e:
            logging.error(f"通知送信エラー: {e}")

    def is_process_running(self):
        """プロセスが実行中かチェック"""
        for proc in psutil.process_iter(['name']):
            try:
                if self.process_name.lower() in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def stop_monitoring(self):
        """モニタリングを停止"""
        self.running = False
        self.icon.stop()

    def start_monitoring(self):
        """モニタリングを開始"""
        logging.info(f"モニタリングを開始します... (プロセス名: {self.process_name})")
        last_status = None

        while self.running:
            try:
                current_status = self.is_process_running()

                # ステータス変更を検知
                if last_status is not None and last_status != current_status:
                    if not current_status:
                        self.send_notification(
                            "TikTok LIVE Studio アラート",
                            "アプリケーションが終了しました。認証が必要な可能性があります。"
                        )
                    else:
                        logging.info("アプリケーションが再起動されました")

                last_status = current_status
                time.sleep(self.check_interval)

            except Exception as e:
                logging.error(f"モニタリングエラー: {e}")
                time.sleep(self.check_interval)

def load_config():
    """設定ファイルを読み込む"""
    config_path = os.path.join(os.path.expanduser('~'), '.tiktok_monitor_config.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"設定ファイルの読み込みに失敗しました: {e}")
    return None

def main():
    # ログ設定
    log_path = os.path.join(os.path.expanduser('~'), 'tiktok_monitor.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # 設定を読み込む
    config = load_config()

    # 初回起動時または設定がない場合は設定ダイアログを表示
    if config is None:
        dialog = SetupDialog()
        config = dialog.run()
        if config is None:
            logging.error("設定が完了していません。アプリケーションを終了します。")
            return

    # モニタリング開始
    monitor = SimpleMonitor(config)

    # モニタリングを別スレッドで開始
    monitoring_thread = threading.Thread(target=monitor.start_monitoring, daemon=True)
    monitoring_thread.start()

    # システムトレイアイコンを表示
    monitor.icon.run()

if __name__ == "__main__":
    main()