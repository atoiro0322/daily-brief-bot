お# 🤖 AI Daily Digest

毎朝、AI・テクノロジーの最新ニュースと論文をまとめてメール配信する自動化ツールです。
**完全無料**で動作します（Gemini API無料枠 + Gmail SMTP + GitHub Actions）。

## ✨ 主な機能

- ✅ **arXiv論文の自動収集** - AI・機械学習の最新論文を毎日取得
- ✅ **RSSフィードからニュース取得** - 複数のテックメディアから自動収集
- ✅ **Google News検索** - キーワードベースで最新ニュースを取得
- ✅ **Gemini AIによる要約** - 重要度スコアリング＆日本語サマリー生成
- ✅ **HTMLメール自動送信** - 見やすいフォーマットで毎朝配信
- ✅ **完全YAML設定** - コード変更不要でカスタマイズ可能
- ✅ **GitHub Actions対応** - 無料で毎日自動実行

---

## 📧 送信されるメールの例

```
┌──────────────────────────────────────┐
│  🤖 AI Daily Digest                  │
│  2026年3月8日                        │
├──────────────────────────────────────┤
│  📋 今日のサマリー                    │
│  ・機械学習の新手法が発表される      │
│  ・OpenAIが新機能をリリース          │
│  ・AI倫理に関する議論が活発化        │
├──────────────────────────────────────┤
│  📰 TOP 5 ニュース                   │
│  1. [90点] タイトル...               │
│  2. [85点] タイトル...               │
├──────────────────────────────────────┤
│  📚 TOP 5 論文                       │
│  1. [95点] 論文タイトル...           │
│  2. [88点] 論文タイトル...           │
└──────────────────────────────────────┘
```

---

## 🚀 クイックスタート

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
3. 「アプリを選択」→「その他」→「AI Daily Digest」と入力
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

1. **Actions** タブ → **AI Daily Digest** ワークフロー
2. **Run workflow** → **Run workflow** をクリック
3. ✅ が表示されたら成功。メールボックスを確認！

---

## ⚙️ カスタマイズ

すべての設定は `config.yaml` で管理します。**Pythonコードの編集は不要**です。

### 興味のあるキーワードに変更

```yaml
keywords:
  # arXiv論文検索用
  arxiv:
    - "artificial intelligence"
    - "machine learning"
    - "your keyword here"  # ← 追加

  # Google News検索用（英語）
  google_news_en:
    - "AI"
    - "technology"
    - "your topic"  # ← 追加

  # Google News検索用（日本語）
  google_news_jp:
    - "AI"
    - "人工知能"
    - "あなたのキーワード"  # ← 追加
```

### ニュースソースを追加

```yaml
feeds:
  english:
    - name: "Your Favorite Tech Blog"
      url: "https://example.com/feed/"
      enabled: true  # ← 追加
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

```yaml
arxiv:
  categories:
    - "cs.AI"   # Artificial Intelligence
    - "cs.LG"   # Machine Learning
    - "cs.CL"   # Computation and Language
    - "cs.CV"   # Computer Vision
    - "cs.RO"   # Robotics
```

全カテゴリ一覧：https://arxiv.org/category_taxonomy

---

## 💰 料金（完全無料！）

| サービス | 無料枠 | 使用量 | 料金 |
|----------|--------|--------|------|
| **Gemini API** | 1,500リクエスト/日 | 1回/日 | **$0** |
| **Gmail SMTP** | 500通/日 | 1通/日 | **$0** |
| **GitHub Actions** | 2,000分/月 | 約30分/月 | **$0** |
| **合計** | ー | ー | **$0 / 月** |

---

## 🖥️ ローカルで実行する場合

```bash
# 1. リポジトリをクローン
git clone https://github.com/YOUR_USERNAME/ai-daily-digest.git
cd ai-daily-digest

# 2. ライブラリをインストール
pip install -r requirements.txt

# 3. .envファイルを作成
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_digit_password
TO_EMAIL=recipient@example.com
EOF

# 4. config.yamlを編集（必要に応じて）
vim config.yaml

# 5. テスト実行（1回だけ送信）
python ai_daily_digest_gemini.py

# 6. 毎日自動実行（常時起動が必要）
python ai_daily_digest_gemini.py --schedule
```

---

## 📁 ファイル構成

```
ai-daily-digest/
├── ai_daily_digest_gemini.py    # メインスクリプト
├── config.yaml                   # 設定ファイル（キーワード・フィード管理）
├── requirements.txt              # 依存パッケージ
├── .github/
│   └── workflows/
│       └── daily_digest.yml     # GitHub Actionsワークフロー
├── .env.example                 # 環境変数テンプレート
└── README.md                    # このファイル
```

---

## 🔧 高度な設定

### NewsAPIを使う

より多くのニュースソースから情報を取得したい場合、NewsAPIを使えます（無料版：100リクエスト/日）。

1. https://newsapi.org/ でAPIキーを取得
2. `.env` に `NEWSAPI_KEY=your_key` を追加
3. `config.yaml` で有効化：

```yaml
newsapi:
  enabled: true
  keywords:
    - "artificial intelligence"
    - "machine learning"
  sources:
    - "techcrunch"
    - "wired"
```

### 複数の設定ファイルを使い分ける

トピックごとに異なる設定を作成できます：

```bash
# カスタム設定ファイルを作成
cp config.yaml config_robotics.yaml
# config_robotics.yaml を編集

# 実行時に指定
python ai_daily_digest_gemini.py --config config_robotics.yaml
```

---

## 🔧 トラブルシューティング

### GitHub Actionsが失敗する

1. **Actions** タブ → 失敗したワークフローをクリック
2. 赤い ✗ のステップを展開してエラーを確認

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

## 📝 カスタマイズ例

### 例1: ロボティクス特化

```yaml
keywords:
  arxiv:
    - "robotics"
    - "autonomous robot"
    - "path planning"
  google_news_en:
    - "robotics"
    - "robot"

arxiv:
  categories:
    - "cs.RO"  # Robotics
    - "cs.AI"
```

### 例2: 自然言語処理特化

```yaml
keywords:
  arxiv:
    - "natural language processing"
    - "LLM"
    - "transformer"
  google_news_en:
    - "ChatGPT"
    - "large language model"

arxiv:
  categories:
    - "cs.CL"  # Computation and Language
    - "cs.AI"
```

### 例3: コンピュータビジョン特化

```yaml
keywords:
  arxiv:
    - "computer vision"
    - "image recognition"
    - "object detection"
  google_news_en:
    - "computer vision"
    - "image AI"

arxiv:
  categories:
    - "cs.CV"  # Computer Vision
    - "cs.AI"
```

---

## 🤝 コントリビューション

Issue・Pull Request大歓迎です！

---

## 📜 ライセンス

MIT License

---

## 🙏 謝辞

- [Google Gemini API](https://ai.google.dev/)
- [arXiv.org](https://arxiv.org/)
- [GitHub Actions](https://github.com/features/actions)

---

**気に入ったら ⭐ をお願いします！**
