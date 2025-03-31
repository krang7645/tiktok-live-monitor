import os
import time
import psutil
import logging
from datetime import datetime
from plyer import notification
from dotenv import load_dotenv

class SimpleMonitor:
    def __init__(self):
        self.process_name = os.getenv('TIKTOK_PROCESS_NAME', 'TikTokLiveStudio')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 30))
        self.last_notification_time = None
        self.notification_cooldown = int(os.getenv('NOTIFICATION_COOLDOWN', 300))

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

    def start_monitoring(self):
        """モニタリングを開始"""
        logging.info(f"モニタリングを開始します... (プロセス名: {self.process_name})")
        last_status = None

        while True:
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

            except KeyboardInterrupt:
                logging.info("モニタリングを終了します")
                break
            except Exception as e:
                logging.error(f"モニタリングエラー: {e}")
                time.sleep(self.check_interval)

def main():
    # 環境変数の読み込み
    load_dotenv()

    # ログ設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # モニタリング開始
    monitor = SimpleMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()