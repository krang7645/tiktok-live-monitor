import os
from plyer import notification
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

class NotificationManager:
    def __init__(self):
        self._line_bot_api = None
        self._line_user_id = None
        self._initialize_line()

    def _initialize_line(self):
        """LINE通知の初期化"""
        line_channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self._line_user_id = os.getenv('LINE_USER_ID')

        if line_channel_access_token and self._line_user_id:
            self._line_bot_api = LineBotApi(line_channel_access_token)

    def send_desktop_notification(self, title, message):
        """デスクトップ通知を送信"""
        notification.notify(
            title=title,
            message=message,
            app_icon=None,
            timeout=10,
        )

    def send_line_notification(self, title, message):
        """LINE通知を送信"""
        if not self._line_bot_api or not self._line_user_id:
            print("LINE通知の設定が完了していません")
            return False

        try:
            self._line_bot_api.push_message(
                self._line_user_id,
                TextSendMessage(text=f"{title}\n{message}")
            )
            return True
        except LineBotApiError as e:
            print(f"LINE通知の送信に失敗しました: {e}")
            return False

    def send_notification(self, method, title, message):
        """指定された方法で通知を送信"""
        notification_methods = {
            'desktop': self.send_desktop_notification,
            'line': self.send_line_notification,
        }

        if method in notification_methods:
            return notification_methods[method](title, message)
        else:
            print(f"未対応の通知方法です: {method}")
            return False