# Daily Brief Bot

興味のあるトピックのニュースと論文を自動収集し、AIで要約して毎朝メールで届けるBotです。
**完全無料**で動作します（Gemini API無料枠 + Gmail SMTP + GitHub Actions）。

キーワードやRSSフィードを `config.yaml` で設定するだけで、あなた専用のデイリーブリーフィングが届きます。

## 主な機能

- **RSSフィードからニュース取得** — 好きなメディアを自由に追加
- **Google News検索** — キーワードベースで最新ニュースを自動収集
- **arXiv論文の自動収集** — 興味のある分野の最新論文を毎日取得
- **AIによる要約** — 重要度スコアリング＆日本語サマリーを自動生成
- **HTMLメール自動送信** — 見やすいフォーマットで毎朝配信
- **完全YAML設定** — コード変更不要でカスタマイズ可能
- **GitHub Actions対応** — 無料で毎日自動実行

---

## 送信されるメールの例

```
┌──────────────────────────────────────┐
│  Daily Brief Bot                      │
│  ****年**月**日                        │
├──────────────────────────────────────┤
│  📋 今日のサマリー                    │
│  ・主要なトレンドの概要              │
│  ・注目すべき出来事の要約            │
│  ・今日押さえておきたいポイント      │
├──────────────────────────────────────┤
│  🌏 海外ニュース TOP5               │
│  1. タイトル...               │
│  2. タイトル...               │
├──────────────────────────────────────┤
│  🇯🇵 国内ニュース TOP5               │
│  1. タイトル...               │
│  2. タイトル...               │
├──────────────────────────────────────┤
│  📚 注目論文 TOP5                    │
│  1. 論文タイトル...           │
│  2. 論文タイトル...           │
├──────────────────────────────────────┤
│  💡 今日のインサイト                  │
│  全体を踏まえたトレンド考察          │
└──────────────────────────────────────┘
```

---

## クイックスタート

### 1. リポジトリをFork

このリポジトリを自分のGitHubアカウントにForkします。

### 2. 必要なAPIキーを取得

#### Gemini API（無料）
1. https://aistudio.google.com/apikey にアクセス
2. 「Create API Key」をクリック
3. APIキーをコピー

#### Gmail アプリパスワード（無料）
1. Googleアカウントにログイン
2. https://myaccount.google.com/apppasswords にアクセス
3. 「アプリを選択」→「その他」→「Daily Brief Bot」と入力
4. 「生成」をクリックして16桁のパスワードをコピー

### 3. GitHub Secretsに設定

リポジトリの **Settings** → **Secrets and variables** → **Actions** → **New repository secret** で以下を追加：

| 名前 | 値 |
|------|-----|
| `GEMINI_API_KEY` | Gemini APIキー |
| `GMAIL_USER` | 送信元Gmailアドレス（例：`your@gmail.com`） |
| `GMAIL_APP_PASSWORD` | Gmailアプリパスワード（16桁・スペースなし） |
| `TO_EMAIL` | 送信先メールアドレス |

### 4. GitHub Actionsを有効化

1. リポジトリの **Actions** タブをクリック
2. 「I understand my workflows, go ahead and enable them」をクリック

### 5. 動作確認

1. **Actions** タブ → **Daily Brief Bot** ワークフロー
2. **Run workflow** → **Run workflow** をクリック
3. 完了したらメールボックスを確認

---

## カスタマイズ

すべての設定は `config.yaml` で管理します。**Pythonコードの編集は不要**です。

### キーワードを変更する

`config.yaml` のキーワードを自分の興味に合わせて変更するだけで、収集するニュースの内容が変わります。

```yaml
keywords:
  # arXiv論文検索用
  arxiv:
    - "your research topic"
    - "another keyword"

  # Google News検索用（英語）
  google_news_en:
    - "your interest"
    - "another topic"

  # Google News検索用（日本語）
  google_news_jp:
    - "あなたの興味"
    - "別のキーワード"
```

### ニュースソースを追加・変更する

```yaml
feeds:
  english:
    - name: "Your Favorite Blog"
      url: "https://example.com/feed/"
      enabled: true

  japanese:
    - name: "好きなメディア"
      url: "https://example.jp/rss/"
      enabled: true
```

### 送信時刻を変更

`.github/workflows/daily_digest.yml` を編集：

```yaml
schedule:
  - cron: '0 22 * * *'  # 毎朝7時(JST) = 22時(UTC)
```

| 送信時刻 (JST) | cron設定 (UTC) |
|----------------|----------------|
| 毎朝 6:00 | `0 21 * * *` |
| 毎朝 7:00 | `0 22 * * *` |
| 毎朝 8:00 | `0 23 * * *` |

### arXivカテゴリを変更

興味のある研究分野のカテゴリを設定できます。

```yaml
arxiv:
  categories:
    - "cs.AI"   # Artificial Intelligence
    - "cs.LG"   # Machine Learning
    - "cs.RO"   # Robotics
    - "econ.GN"  # General Economics
    - "q-bio.NC" # Neurons and Cognition
```

全カテゴリ一覧：https://arxiv.org/category_taxonomy

---

## 料金（完全無料）

| サービス | 無料枠 | 使用量 | 料金 |
|----------|--------|--------|------|
| **Gemini API** | 1,500リクエスト/日 | 1回/日 | **$0** |
| **Gmail SMTP** | 500通/日 | 1通/日 | **$0** |
| **GitHub Actions** | 2,000分/月 | 約30分/月 | **$0** |
| **合計** | — | — | **$0 / 月** |

---

## ローカルで実行する場合

```bash
# 1. リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/daily-brief-bot.git
cd daily-brief-bot

# 2. ライブラリをインストール
pip install -r requirements.txt

# 3. .envファイルを作成
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_password
TO_EMAIL=recipient@example.com
EOF

# 4. config.yamlを編集（キーワード・フィードを自分用に変更）
vim config.yaml

# 5. テスト実行（1回だけ送信）
python ai_daily_digest_gemini.py

# 6. 毎日自動実行（常時起動が必要）
python ai_daily_digest_gemini.py --schedule
```

---

## ファイル構成

```
daily-brief-bot/
├── ai_daily_digest_gemini.py    # メインスクリプト
├── config.yaml                   # 設定ファイル（キーワード・フィード管理）
├── requirements.txt              # 依存パッケージ
├── .github/
│   └── workflows/
│       └── daily_digest.yml     # GitHub Actionsワークフロー
├── .env.example                 # 環境変数テンプレート
└── README.md
```

---

## 高度な設定

### NewsAPIを使う

より多くのニュースソースから情報を取得したい場合、NewsAPIを使えます（無料版：100リクエスト/日）。

1. https://newsapi.org/ でAPIキーを取得
2. `.env` に `NEWSAPI_KEY=your_key` を追加
3. `config.yaml` で有効化：

```yaml
newsapi:
  enabled: true
  keywords:
    - "your keyword"
    - "another topic"
  sources:
    - "techcrunch"
    - "wired"
```

### 複数の設定ファイルを使い分ける

トピックごとに異なる設定を作成できます：

```bash
# カスタム設定ファイルを作成
cp config.yaml config_finance.yaml
# config_finance.yaml を編集

# 実行時に指定
python ai_daily_digest_gemini.py --config config_finance.yaml
```

---

## トラブルシューティング

### GitHub Actionsが失敗する

1. **Actions** タブ → 失敗したワークフローをクリック
2. 赤いステップを展開してエラーを確認

### よくあるエラー

| エラー | 原因 | 対処法 |
|--------|------|--------|
| `Authentication failed` | Gmailアプリパスワードが間違い | Secretsを再確認 |
| `API key not valid` | Gemini APIキーが間違い | Secretsを再確認 |
| `No module named 'yaml'` | ライブラリ未インストール | `pip install -r requirements.txt` |
| メールが届かない | TO_EMAILが未設定 | SecretにTO_EMAILを追加 |

### メールが迷惑メールに入る

Gmail設定で送信元アドレスを連絡先に追加してください。

---

## カスタマイズ例

### 例1: テクノロジー全般

```yaml
keywords:
  arxiv:
    - "artificial intelligence"
    - "machine learning"
  google_news_en:
    - "technology"
    - "startup"
  google_news_jp:
    - "テクノロジー"
    - "スタートアップ"

feeds:
  english:
    - name: "TechCrunch"
      url: "https://techcrunch.com/feed/"
      enabled: true
```

### 例2: 金融・経済

```yaml
keywords:
  arxiv:
    - "quantitative finance"
    - "financial modeling"
  google_news_en:
    - "stock market"
    - "fintech"
  google_news_jp:
    - "株式市場"
    - "金融"

arxiv:
  categories:
    - "q-fin.ST"  # Statistical Finance
    - "q-fin.PM"  # Portfolio Management
```

### 例3: ロボティクス

```yaml
keywords:
  arxiv:
    - "robotics"
    - "autonomous robot"
    - "path planning"
  google_news_en:
    - "robotics"
    - "autonomous vehicle"
  google_news_jp:
    - "ロボット"
    - "自動運転"

arxiv:
  categories:
    - "cs.RO"  # Robotics
    - "cs.SY"  # Systems and Control
```

### 例4: 医療・バイオ

```yaml
keywords:
  arxiv:
    - "biomedical"
    - "drug discovery"
  google_news_en:
    - "healthcare technology"
    - "biotech"
  google_news_jp:
    - "医療テクノロジー"
    - "バイオテック"

arxiv:
  categories:
    - "q-bio.BM"  # Biomolecules
    - "cs.AI"
```

---

## コントリビューション

Issue・Pull Request大歓迎です！

---

## ライセンス

MIT License

---

## 謝辞

- [Google Gemini API](https://ai.google.dev/)
- [arXiv.org](https://arxiv.org/)
- [GitHub Actions](https://github.com/features/actions)
