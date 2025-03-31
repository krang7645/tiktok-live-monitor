import cv2
import numpy as np
import pyautogui
import time
from plyer import notification
import os
from datetime import datetime
from dotenv import load_dotenv
from notifiers import NotificationManager

class TikTokLiveMonitor:
    def __init__(self):
        self.auth_screen_template = None
        self.notification_manager = NotificationManager()

    def load_template(self, template_path):
        """認証画面のテンプレート画像を読み込む"""
        if os.path.exists(template_path):
            self.auth_screen_template = cv2.imread(template_path)
            return True
        return False

    def capture_screen(self):
        """画面をキャプチャする"""
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def detect_auth_screen(self, screen):
        """認証画面を検出する"""
        if self.auth_screen_template is None:
            return False

        result = cv2.matchTemplate(screen, self.auth_screen_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        return max_val > 0.8

    def start_monitoring(self, check_interval=30, notification_methods=None):
        """モニタリングを開始"""
        if notification_methods is None:
            notification_methods = ['desktop']

        print("モニタリングを開始しました...")
        last_notification_time = None
        notification_cooldown = 300  # 5分間の通知クールダウン

        while True:
            try:
                screen = self.capture_screen()
                current_time = datetime.now()

                if self.detect_auth_screen(screen):
                    if (last_notification_time is None or
                        (current_time - last_notification_time).total_seconds() > notification_cooldown):

                        print(f"認証画面を検出: {current_time}")

                        for method in notification_methods:
                            self.notification_manager.send_notification(
                                method,
                                "TikTok LIVE Studio認証必要",
                                "TikTok LIVE Studioの再認証が必要です"
                            )

                        last_notification_time = current_time

                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("モニタリングを終了します")
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                time.sleep(check_interval)

def main():
    load_dotenv()

    monitor = TikTokLiveMonitor()
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'auth_screen.png')

    if not monitor.load_template(template_path):
        print(f"警告: テンプレート画像が見つかりません: {template_path}")
        print("認証画面のスクリーンショットを templates/auth_screen.png として保存してください")
        return

    # 使用する通知方法を指定
    notification_methods = ['desktop', 'line']  # 'sound', 'email' なども追加可能

    # モニタリング開始
    monitor.start_monitoring(
        check_interval=30,
        notification_methods=notification_methods
    )

if __name__ == "__main__":
    main()