<<<<<<< HEAD
# TikTok LIVE Studio 認証監視システム

TikTok LIVE Studioの認証画面を監視し、再認証が必要になった際に通知を送信するシステムです。

## 機能

- 画面キャプチャによる認証画面の自動検出
- 複数の通知方法をサポート
  - デスクトップ通知
  - LINE通知
- 通知のクールダウン機能（重複通知防止）

## セットアップ

1. 必要なパッケージをインストール：
```bash
pip install -r requirements.txt
```

2. 環境変数の設定：
   - `.env.example`を`.env`にコピー
   - LINE通知を使用する場合は、LINE Developersで取得したトークンとユーザーIDを設定

3. 認証画面のテンプレート画像を準備：
   - TikTok LIVE Studioの認証画面のスクリーンショットを撮影
   - `templates/auth_screen.png`として保存

## 使用方法

1. プログラムを起動：
```bash
python monitor.py
```

2. バックグラウンドで実行する場合：
```bash
nohup python monitor.py &
```

## 設定項目

- `CHECK_INTERVAL`: 画面チェックの間隔（秒）
- `NOTIFICATION_COOLDOWN`: 通知の最小間隔（秒）
- 通知方法の選択：`monitor.py`の`notification_methods`リストを編集

## 注意事項

- CPU使用率を抑えるため、チェック間隔は適切な値に設定してください
- LINE通知を使用する場合は、LINE Developersでの設定が必要です
- テンプレート画像は実際の認証画面と一致している必要があります
=======
# tiktok-live-monitor
TikTok LIVE Studio Monitor - A monitoring tool for TikTok LIVE Studio
>>>>>>> e3a9ec2e100e8bb5a48d57adf3361738cedde2c0
