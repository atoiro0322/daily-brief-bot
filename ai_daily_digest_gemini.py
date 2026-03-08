"""
AI Daily Digest - Gemini API + 設定ファイル版
=====================================================================
config.yaml から設定を読み込んで動作します。
キーワードやフィードの追加・変更はconfig.yamlを編集するだけでOK。

主な機能:
  ✓ 設定ファイル（config.yaml）でキーワード・フィードを管理
  ✓ enabled フラグでフィードを簡単にON/OFF
  ✓ Google News検索URLを動的生成
  ✓ 複数の設定ファイルに対応（--config で切り替え）

メール構成:
  🌏 海外ニュース TOP5（複数ソースから厳選・日本語要約）
  🇯🇵 国内ニュース TOP5（複数ソースから厳選）
  📄 注目論文 TOP5（arXivから）
  💡 今日のインサイト

必要なライブラリ:
    pip install -r requirements.txt
    # または
    pip install google-generativeai requests python-dotenv feedparser pyyaml

必要な環境変数 (.env ファイルに記載):
    GEMINI_API_KEY=your_gemini_api_key
    GMAIL_USER=your_gmail@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    TO_EMAIL=recipient@gmail.com

必要な設定ファイル:
    config.yaml（キーワード・フィード・基本設定）

実行方法:
    python ai_daily_digest_gemini.py                    # 即座に実行
    python ai_daily_digest_gemini.py --schedule         # 毎朝自動送信
    python ai_daily_digest_gemini.py --config my.yaml  # カスタム設定使用

Gemini APIキー取得:      https://aistudio.google.com/app/apikey
Gmailアプリパスワード:   https://myaccount.google.com/apppasswords
"""

import google.generativeai as genai
import requests
import feedparser
import re
import schedule
import time
import smtplib
import argparse
import yaml
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import calendar
from pathlib import Path

# NewsAPIのインポート（オプション）
try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    print("[警告] newsapi-pythonがインストールされていません。NewsAPI機能は無効です。")

load_dotenv()

# =====================================================================
# 設定ファイル読み込み
# =====================================================================
def load_config(config_path: str = "config.yaml") -> dict:
    """YAMLファイルから設定を読み込む"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"✓ 設定ファイルを読み込みました: {config_path}")
    return config

# グローバル設定
CONFIG = load_config()

# =====================================================================
# 設定
# =====================================================================
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")
GMAIL_USER         = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL           = os.getenv("TO_EMAIL", GMAIL_USER)

# config.yamlから設定を取得
SETTINGS           = CONFIG["settings"]
SEND_TIME          = SETTINGS["send_time"]
GEMINI_MODEL       = SETTINGS["gemini_model"]
NEWS_FETCH_PER_FEED = SETTINGS["news_fetch_per_feed"]
NEWS_TOP_N         = SETTINGS["news_top_n"]
PAPER_TOP_N        = SETTINGS["paper_top_n"]

KEYWORDS           = CONFIG["keywords"]
ARXIV_CONFIG       = CONFIG["arxiv"]
FEEDS              = CONFIG["feeds"]


# =====================================================================
# Google News URL 動的生成
# =====================================================================
def build_google_news_url(keywords: list[str], language: str) -> str:
    """キーワードリストからGoogle News RSS URLを生成"""
    if language == "en":
        query = "+".join([kw.replace(" ", "+") for kw in keywords])
        return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    else:  # jp
        query = "+OR+".join(keywords)
        return f"https://news.google.com/rss/search?q={query}&hl=ja&gl=JP&ceid=JP:ja"


def get_active_feeds(feed_list: list[dict]) -> list[dict]:
    """有効なフィードのみを抽出し、Google News URLを動的生成"""
    active_feeds = []
    for feed in feed_list:
        if not feed.get("enabled", True):
            continue

        # Google News検索の場合はURL動的生成
        if feed.get("type") == "google_news":
            keyword_key = feed.get("use_keywords")
            keywords = KEYWORDS.get(keyword_key, [])
            language = feed.get("language", "en")
            feed["url"] = build_google_news_url(keywords, language)

        active_feeds.append(feed)

    return active_feeds


# =====================================================================
# NewsAPI 取得
# =====================================================================
def fetch_from_newsapi() -> list[dict]:
    """NewsAPIから記事を取得する（config.yamlの設定を使用）"""
    newsapi_config = CONFIG.get("newsapi", {})

    # NewsAPIが無効の場合は空リストを返す
    if not newsapi_config.get("enabled", False):
        return []

    # newsapi-pythonがインストールされていない場合
    if not NEWSAPI_AVAILABLE:
        print("    [警告] NewsAPI機能を使用するには newsapi-python をインストールしてください")
        return []

    # APIキーを環境変数から取得
    api_key_env = newsapi_config.get("api_key_env", "NEWSAPI_KEY")
    api_key = os.getenv(api_key_env)

    if not api_key:
        print(f"    [警告] 環境変数 {api_key_env} が設定されていません")
        return []

    try:
        newsapi = NewsApiClient(api_key=api_key)

        # 設定から取得
        keywords = newsapi_config.get("keywords", [])
        sources = newsapi_config.get("sources", [])
        language = newsapi_config.get("language", "en")
        sort_by = newsapi_config.get("sort_by", "publishedAt")
        max_results = newsapi_config.get("max_results", 20)

        # キーワードクエリを構築
        query = " OR ".join(keywords) if keywords else None
        sources_str = ",".join(sources) if sources else None

        # NewsAPIで検索
        print(f"  → NewsAPIから取得中（キーワード: {len(keywords)}個, ソース: {len(sources)}個）...")

        response = newsapi.get_everything(
            q=query,
            sources=sources_str,
            language=language,
            sort_by=sort_by,
            page_size=max_results
        )

        articles = response.get("articles", [])

        # 標準フォーマットに変換
        result = []
        for article in articles:
            result.append({
                "source": article.get("source", {}).get("name", "NewsAPI"),
                "title": article.get("title", "（タイトルなし）"),
                "link": article.get("url", ""),
                "summary": article.get("description", "")[:300],
                "published": article.get("publishedAt", "")[:10],
            })

        print(f"    ✓ NewsAPI: {len(result)}件")
        return result

    except Exception as e:
        print(f"    [警告] NewsAPI取得エラー: {e}")
        return []


# =====================================================================
# ユーティリティ
# =====================================================================
def parse_entry_date(entry) -> datetime:
    """フィードエントリの公開日時をdatetimeに変換する"""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc)
            except Exception:
                pass
    return datetime.min.replace(tzinfo=timezone.utc)


def strip_html(text: str) -> str:
    """HTMLタグを除去してプレーンテキストに変換する"""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def fetch_rss_feed(feed_info: dict, max_items: int) -> list[dict]:
    """RSSフィードを取得してエントリのリストを返す"""
    try:
        feed = feedparser.parse(feed_info["url"])
        entries = sorted(feed.entries, key=parse_entry_date, reverse=True)
        result = []
        for entry in entries[:max_items]:
            summary = strip_html(getattr(entry, "summary", "") or "")[:300]
            result.append({
                "source":    feed_info["name"],
                "title":     getattr(entry, "title",  "（タイトルなし）"),
                "link":      getattr(entry, "link",   ""),
                "summary":   summary,
                "published": parse_entry_date(entry).strftime("%Y-%m-%d"),
            })
        return result
    except Exception as e:
        print(f"    [警告] {feed_info['name']} 取得失敗: {e}")
        return []


# =====================================================================
# Step 1: ニュース取得
# =====================================================================
def fetch_en_news() -> list[dict]:
    """英語ニュースを取得する（RSS + NewsAPI）"""
    print("  → 英語ニュースを取得中...")
    all_items = []

    # RSSフィードから取得
    active_feeds = get_active_feeds(FEEDS["english"])
    for feed in active_feeds:
        items = fetch_rss_feed(feed, NEWS_FETCH_PER_FEED)
        all_items.extend(items)
        print(f"    ✓ {feed['name']}: {len(items)}件")

    # NewsAPIから取得（有効な場合）
    newsapi_items = fetch_from_newsapi()
    if newsapi_items:
        all_items.extend(newsapi_items)

    all_items.sort(key=lambda x: x["published"], reverse=True)
    return all_items


def fetch_jp_news() -> list[dict]:
    """日本語ニュースを取得する（config.yamlから有効なフィードのみ）"""
    print("  → 日本語ニュースを取得中...")
    active_feeds = get_active_feeds(FEEDS["japanese"])
    all_items = []
    for feed in active_feeds:
        items = fetch_rss_feed(feed, NEWS_FETCH_PER_FEED)
        all_items.extend(items)
        print(f"    ✓ {feed['name']}: {len(items)}件")
    all_items.sort(key=lambda x: x["published"], reverse=True)
    return all_items


# =====================================================================
# Step 2: arXiv 論文取得
# =====================================================================
def fetch_arxiv_papers(max_results: int = None) -> list[dict]:
    """arXiv APIから論文を取得する（config.yamlのキーワード・カテゴリを使用）"""
    if max_results is None:
        max_results = ARXIV_CONFIG["max_results"]

    print("  → arXiv APIから論文を取得中...")

    keywords = KEYWORDS["arxiv"]
    categories = ARXIV_CONFIG["categories"]

    query_terms     = " OR ".join([f'"{kw}"' for kw in keywords])
    category_filter = " OR ".join([f"cat:{c}" for c in categories])
    query = f"({query_terms}) AND ({category_filter})"

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    try:
        resp = requests.get(
            "http://export.arxiv.org/api/query",
            params=params,
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"    [警告] arXiv取得エラー: {e}")
        return []

    feed = feedparser.parse(resp.text)
    papers = []
    for entry in feed.entries:
        papers.append({
            "title":     entry.title.replace("\n", " ").strip(),
            "authors":   ", ".join(a.name for a in entry.authors[:3]),
            "summary":   entry.summary[:400].replace("\n", " ").strip(),
            "link":      entry.link,
            "published": entry.published[:10],
        })
    print(f"    ✓ arXiv: {len(papers)}件")
    return papers


# =====================================================================
# Step 3: Gemini API でHTMLダイジェスト生成
# =====================================================================
def format_news_for_prompt(items: list[dict], top_n: int) -> str:
    """ニュースリストをプロンプト用テキストに変換する（多めに渡してGeminiに厳選させる）"""
    return "\n\n".join([
        f"[{i+1}] {item['title']}\n"
        f"ソース: {item['source']} | 日付: {item['published']}\n"
        f"概要: {item['summary']}\n"
        f"URL: {item['link']}"
        for i, item in enumerate(items[:top_n * 3])
    ]) or "（本日のニュースなし）"


def format_papers_for_prompt(papers: list[dict], top_n: int) -> str:
    """論文リストをプロンプト用テキストに変換する"""
    return "\n\n".join([
        f"[{i+1}] {p['title']}\n"
        f"著者: {p['authors']} | 投稿日: {p['published']}\n"
        f"概要: {p['summary']}\n"
        f"URL: {p['link']}"
        for i, p in enumerate(papers[:top_n * 2])
    ]) or "（本日の新着論文なし）"


def generate_digest_with_gemini(
    en_news: list[dict],
    jp_news: list[dict],
    papers:  list[dict],
) -> str:
    """Gemini APIでHTMLダイジェストメールを生成する（1リクエスト）"""
    print(f"  → Gemini API ({GEMINI_MODEL}) でダイジェスト生成中...")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    today = datetime.now().strftime("%Y年%m月%d日")

    # 有効なソース名を取得
    en_sources = [f["name"] for f in get_active_feeds(FEEDS["english"])]
    jp_sources = [f["name"] for f in get_active_feeds(FEEDS["japanese"])]
    all_sources = " / ".join(en_sources + jp_sources + ["arXiv"])

    prompt = f"""
あなたは自動運転・AI技術の専門リサーチャーです。
以下の情報をもとに、{today}付けの日本語ダイジェストメール（HTML形式）を生成してください。

=== 🌏 海外ニュース候補 ===
{format_news_for_prompt(en_news, NEWS_TOP_N)}

=== 🇯🇵 国内ニュース候補 ===
{format_news_for_prompt(jp_news, NEWS_TOP_N)}

=== 📄 arXiv 論文候補 ===
{format_papers_for_prompt(papers, PAPER_TOP_N)}

## 出力ルール
- HTMLのみ出力する（マークダウン・説明文・コードブロック記法 ``` は不要）
- 日本語で記述する
- 英語記事のタイトル・要約は日本語に翻訳する

## メール構成（各セクションTOP{NEWS_TOP_N}を掲載）

### 1. ヘッダー
- タイトル:「🤖 AI & 自動運転 デイリーダイジェスト」と {today}

### 2. 📋 今日のサマリー
- 海外・国内・論文を横断した今日の主要トレンドを3〜4文で概説

### 3. 🌏 海外ニュース TOP{NEWS_TOP_N}
- 自動運転・AIエンジニアへの重要度・新規性で上位{NEWS_TOP_N}件を厳選
- 各記事の表示項目:
  ① 日本語タイトル（英語原文を翻訳）
  ② ソース名 | 日付
  ③ 日本語要約（2文）
  ④「元記事を読む →」リンク

### 4. 🇯🇵 国内ニュース TOP{NEWS_TOP_N}
- 上位{NEWS_TOP_N}件を厳選
- 各記事の表示項目:
  ① タイトル
  ② ソース名 | 日付
  ③ 要約（2文）
  ④「記事を読む →」リンク

### 5. 📄 注目論文 TOP{PAPER_TOP_N}
- 上位{PAPER_TOP_N}件を厳選
- 各論文の表示項目:
  ① 日本語タイトル（英語原文を翻訳）
  ② 著者 | 投稿日
  ③ 日本語要約（2〜3文）
  ④「arXivで読む →」リンク

### 6. 💡 今日のインサイト
- 全体を踏まえた技術トレンドの考察を3〜4文

### 7. フッター
- 配信日時
- ソース一覧: {all_sources}

## デザイン仕様（インラインCSSを使用）
- 全体背景: #f0f4f8
- コンテナ: max-width 640px, margin 0 auto, background #ffffff, border-radius 8px
- ヘッダー: background linear-gradient(135deg,#1e3a5f,#2563eb), color #fff, padding 32px 24px
- セクション: padding 20px 24px
- セクション見出し: color #1e3a5f, border-left 4px solid #2563eb, padding-left 12px, margin-bottom 16px
- サマリーボックス: background #eff6ff, border-radius 6px, padding 16px, margin-bottom 8px
- 海外ニュースカード: background #f8fafc, border-radius 6px, border-left 3px solid #60a5fa, padding 14px, margin-bottom 10px
- 国内ニュースカード: background #faf5ff, border-radius 6px, border-left 3px solid #a78bfa, padding 14px, margin-bottom 10px
- 論文カード: background #f0fdf4, border-radius 6px, border-left 3px solid #34d399, padding 14px, margin-bottom 10px
- インサイトボックス: background #fefce8, border-radius 6px, padding 16px
- カードタイトル: font-weight bold, color #1e3a5f, font-size 14px, margin-bottom 4px
- メタ情報（ソース・日付）: font-size 11px, color #6b7280, margin-bottom 6px
- リンク: color #2563eb, font-size 12px, text-decoration none
- フォント: Arial, sans-serif, font-size 13px, line-height 1.7
- フッター: background #f1f5f9, padding 16px 24px, font-size 11px, color #9ca3af, border-radius 0 0 8px 8px
"""

    try:
        response = model.generate_content(prompt)
        html = response.text.strip()
        # コードブロック記法を除去
        html = re.sub(r"```(?:html)?\n?", "", html).strip().rstrip("`").strip()
        return html
    except Exception as e:
        print(f"  [エラー] Gemini API呼び出し失敗: {e}")
        raise


# =====================================================================
# Step 4: Gmail SMTP で送信
# =====================================================================
def send_email(html_content: str):
    """SMTPでGmailからHTMLメールを送信する"""
    today   = datetime.now().strftime("%Y/%m/%d")
    subject = f"【AI Daily】{today} - 自動運転・AI技術 朝刊"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    print(f"  → Gmail SMTPで送信中 → {TO_EMAIL}")
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())
        print(f"  ✅ 送信完了: 「{subject}」")
    except smtplib.SMTPAuthenticationError:
        print("  [エラー] Gmail認証失敗。アプリパスワードを確認してください。")
        raise
    except Exception as e:
        print(f"  [エラー] 送信失敗: {e}")
        raise


# =====================================================================
# メイン処理
# =====================================================================
def run_daily_digest():
    """ダイジェスト生成〜送信を1回実行する"""
    print(f"\n{'='*58}")
    print(f" AI Daily Digest 開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*58}")

    missing = [k for k, v in {
        "GEMINI_API_KEY":     GEMINI_API_KEY,
        "GMAIL_USER":         GMAIL_USER,
        "GMAIL_APP_PASSWORD": GMAIL_APP_PASSWORD,
    }.items() if not v]
    if missing:
        print(f"[エラー] 環境変数が未設定です: {', '.join(missing)}")
        return

    try:
        # 1. ニュース取得
        print("\n[1/4] ニュースを取得中...")
        en_news = fetch_en_news()
        jp_news = fetch_jp_news()
        print(f"      英語: {len(en_news)}件 / 日本語: {len(jp_news)}件")

        # 2. 論文取得
        print("\n[2/4] arXivから論文を取得中...")
        papers = fetch_arxiv_papers(max_results=15)
        print(f"      {len(papers)}件取得")

        # 3. Geminiでダイジェスト生成（1リクエスト）
        print("\n[3/4] Gemini APIでダイジェストを生成中...")
        html_content = generate_digest_with_gemini(en_news, jp_news, papers)
        print(f"      生成完了（{len(html_content):,}文字）")

        # 4. メール送信
        print("\n[4/4] メールを送信中...")
        send_email(html_content)

        print(f"\n{'='*58}")
        print(" ✅ 全処理完了！")
        print(f"{'='*58}\n")

    except Exception as e:
        print(f"\n❌ 処理中にエラーが発生しました: {e}")


# =====================================================================
# スケジューラー
# =====================================================================
def main():
    global CONFIG, SETTINGS, SEND_TIME, GEMINI_MODEL, NEWS_FETCH_PER_FEED, NEWS_TOP_N, PAPER_TOP_N, KEYWORDS, ARXIV_CONFIG, FEEDS

    parser = argparse.ArgumentParser(description="AI Daily Digest（設定ファイル対応版）")
    parser.add_argument(
        "--schedule", action="store_true",
        help="毎朝定期実行する（常時起動モード）",
    )
    parser.add_argument(
        "--config", type=str, default="config.yaml",
        help="設定ファイルのパス（デフォルト: config.yaml）",
    )
    args = parser.parse_args()

    # 設定ファイル再読み込み（引数で指定された場合）
    if args.config != "config.yaml":
        CONFIG = load_config(args.config)
        SETTINGS = CONFIG["settings"]
        SEND_TIME = SETTINGS["send_time"]
        GEMINI_MODEL = SETTINGS["gemini_model"]
        NEWS_FETCH_PER_FEED = SETTINGS["news_fetch_per_feed"]
        NEWS_TOP_N = SETTINGS["news_top_n"]
        PAPER_TOP_N = SETTINGS["paper_top_n"]
        KEYWORDS = CONFIG["keywords"]
        ARXIV_CONFIG = CONFIG["arxiv"]
        FEEDS = CONFIG["feeds"]

    if args.schedule:
        print(f"📅 スケジューラー起動: 毎朝 {SEND_TIME} に送信")
        print("   Ctrl+C で停止\n")
        schedule.every().day.at(SEND_TIME).do(run_daily_digest)
        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_daily_digest()


if __name__ == "__main__":
    main()