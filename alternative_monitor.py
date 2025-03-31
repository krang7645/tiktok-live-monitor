import os
import time
import psutil
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from scapy.all import sniff, IP
from notifiers import NotificationManager
from dotenv import load_dotenv

class TikTokStudioMonitor:
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.log_dir = os.getenv('TIKTOK_LOG_DIR', '')  # TikTok Studio のログディレクトリ
        self.process_name = "TikTokLiveStudio.exe"  # プロセス名
        self.last_notification_time = None
        self.notification_cooldown = int(os.getenv('NOTIFICATION_COOLDOWN', 300))

    def should_notify(self):
        """通知クールダウンチェック"""
        if self.last_notification_time is None:
            return True

        time_diff = (datetime.now() - self.last_notification_time).total_seconds()
        return time_diff > self.notification_cooldown

    def send_notifications(self, title, message, methods=None):
        """通知を送信"""
        if not self.should_notify():
            return

        if methods is None:
            methods = ['desktop', 'line']

        for method in methods:
            self.notification_manager.send_notification(method, title, message)

        self.last_notification_time = datetime.now()

    def monitor_log_files(self):
        """ログファイルの監視"""
        class LogHandler(FileSystemEventHandler):
            def __init__(self, callback):
                self.callback = callback

            def on_modified(self, event):
                if event.is_directory:
                    return
                if event.src_path.endswith('.log'):
                    self.check_log_content(event.src_path)

            def check_log_content(self, log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        last_lines = f.readlines()[-50:]  # 最後の50行を確認
                        for line in last_lines:
                            if "authentication" in line.lower() or "login" in line.lower():
                                self.callback("ログファイルで認証イベントを検出しました")
                except Exception as e:
                    logging.error(f"ログファイル読み取りエラー: {e}")

        if not self.log_dir:
            logging.warning("ログディレクトリが設定されていません")
            return

        event_handler = LogHandler(
            lambda msg: self.send_notifications(
                "TikTok LIVE Studio認証アラート",
                msg
            )
        )
        observer = Observer()
        observer.schedule(event_handler, self.log_dir, recursive=False)
        observer.start()
        return observer

    def monitor_process(self):
        """プロセスの状態を監視"""
        last_status = None

        while True:
            try:
                current_status = False
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == self.process_name:
                        current_status = True
                        break

                if last_status is not None and last_status != current_status:
                    if not current_status:
                        self.send_notifications(
                            "TikTok LIVE Studio状態変更",
                            "プロセスが終了しました - 認証が必要な可能性があります"
                        )

                last_status = current_status
                time.sleep(30)  # 30秒ごとにチェック

            except Exception as e:
                logging.error(f"プロセス監視エラー: {e}")
                time.sleep(30)

    def monitor_network(self):
        """ネットワークトラフィックを監視"""
        def packet_callback(packet):
            if IP in packet:
                if packet[IP].dst.startswith('203.'):  # TikTokのIPアドレス範囲（例）
                    if "authentication" in str(packet).lower():
                        self.send_notifications(
                            "TikTok LIVE Studio認証アラート",
                            "認証関連のネットワークトラフィックを検出しました"
                        )

        try:
            sniff(
                filter="host 203.0.0.0/8",  # TikTokのIPアドレス範囲（例）
                prn=packet_callback,
                store=0
            )
        except Exception as e:
            logging.error(f"ネットワーク監視エラー: {e}")

def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)

    monitor = TikTokStudioMonitor()

    # 監視方法の選択
    monitoring_methods = os.getenv('MONITORING_METHODS', 'process,log').split(',')

    if 'process' in monitoring_methods:
        logging.info("プロセス監視を開始します...")
        monitor.monitor_process()

    if 'log' in monitoring_methods:
        logging.info("ログファイル監視を開始します...")
        observer = monitor.monitor_log_files()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    if 'network' in monitoring_methods:
        logging.info("ネットワークトラフィック監視を開始します...")
        monitor.monitor_network()

if __name__ == "__main__":
    main()