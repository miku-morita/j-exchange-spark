import streamlit as st
import pandas as pd
import os
import hashlib
import hmac
import secrets
import tempfile
import time as clock_time
import re
import calendar
import csv
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, time, date, timedelta, timezone

# ==========================================
# 1. データの準備と設定
# ==========================================
st.set_page_config(page_title="J-EXCHANGE SPARK 管理アプリ", layout="wide")

# 白を基調に、操作する場所を緑で示す共通デザイン。
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Graduate&display=swap');
.stApp { background: #ffffff; color: #24352c; }
/* 白基調を維持し、OS/ブラウザのダーク設定で白文字・白背景が混在するのを防ぐ。 */
.stApp, [data-testid="stHeader"] { color-scheme: light; }
.stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stWidgetLabel"],
.stApp [data-testid="stText"], .stApp [data-testid="stExpander"] summary { color: #24352c; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="textarea"],
[data-baseweb="popover"], [data-baseweb="popover"] li,
[data-testid="stDialog"] [role="dialog"] { background: #ffffff !important; color: #24352c !important; }
[data-baseweb="select"] span, [data-baseweb="popover"] li * { color: #24352c; }
.stButton button, .stFormSubmitButton button { background: #ffffff; color: #24352c; }
.stButton button[kind="primary"] [data-testid="stMarkdownContainer"],
.stFormSubmitButton button[kind="primary"] [data-testid="stMarkdownContainer"] { color: #ffffff; }
.stApp a { color: #14532d; }
[data-testid="stHeader"] { background: #ffffff; }
[data-testid="stMainBlockContainer"] { max-width: 100%; padding: 2rem clamp(1rem, 3vw, 3rem) 4rem; }
[data-testid="stSidebar"] { background: #f4f8f5; border-right: 1px solid #dce9e1; }
[data-testid="stMarkdownContainer"] p { line-height: 1.75; }
[data-testid="stCaptionContainer"] { color: #526158; }
[data-testid="stWidgetLabel"] p { font-weight: 600; }
h1, h2, h3 { color: #30574b; letter-spacing: .015em; font-family: 'Graduate', 'Yu Gothic', 'Meiryo', sans-serif; }
h1 { font-size: 2rem !important; }
h2 { font-size: 1.45rem !important; }
h3 { font-size: 1.15rem !important; margin-top: .7rem; }
[data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] > div {
    background: #ffffff; border-radius: 20px; border-color: #e2e9e3;
}
[data-testid="stForm"] { padding: 1.5rem; box-shadow: 0 6px 24px #30574b08; }
[data-testid="stAlert"] { border-radius: 14px; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div { border-radius: 12px; }
.stButton button, .stFormSubmitButton button {
    border-radius: 12px; min-height: 48px; border-color: #bdcfc2;
    font-weight: 600; transition: background .15s, border-color .15s;
}
.stButton button:hover, .stFormSubmitButton button:hover { border-color: #3c7764; background: #eef7f1; color: #30574b; }
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] { background: #14532D; border-color: #14532D; color: white; }
.stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primary"]:hover { background: #0F4023; color: white; }
.stButton button:focus-visible, .stFormSubmitButton button:focus-visible { outline: 3px solid #14532D; outline-offset: 3px; }
[data-testid="stExpander"] { background: white; border-radius: 14px; }
.spark-welcome {
    background: #f3faf5;
    border: 1px solid #dbeadd; border-left: 5px solid #14532D; border-radius: 16px;
    padding: 1.5rem 1.75rem; margin-bottom: 1.2rem;
}
.spark-brand { color: #14532d; font-family: 'Graduate', serif; font-weight: 900; font-size: 1.05rem; letter-spacing: .06em; }
[data-testid="stSidebar"] h1 { font-family: 'Graduate', serif; font-size: 1.45rem !important; font-weight: 900; line-height: 1.35; }
.spark-welcome h1 { margin: .35rem 0; padding: 0; }
.spark-welcome p { margin: .65rem 0 0; color: #51675f; line-height: 1.8; }
.st-key-page [role="radiogroup"] {
    display: flex; flex-direction: column; gap: .4rem;
    width: 100%; padding: .25rem 0;
}
.st-key-page [role="radiogroup"] > label {
    background: transparent; border: 0; border-left: 3px solid transparent;
    border-radius: 0 !important; width: 100%; box-sizing: border-box;
    white-space: normal; padding: .65rem .9rem;
    min-height: 48px; margin: 0; cursor: pointer;
}
.st-key-page [role="radiogroup"] > label > div:first-child { display: none; }
.st-key-page [role="radiogroup"] > label:hover { background: #f3faf5; }
.st-key-page [role="radiogroup"] > label:has(input:checked) {
    background: #e8f5ec; border-left-color: #14532D; color: #195b33;
    font-weight: 700;
}
.st-key-page [role="radiogroup"] > label:focus-within { outline: 2px solid #3c7764; outline-offset: 3px; }
[data-testid="stTabs"] [role="tab"] { border-radius: 0 !important; }
.st-key-activity-calendar { width: 100%; max-width: 1080px; padding: 0; gap: 0 !important; border-top: 1px solid #c6d2ca; border-left: 1px solid #c6d2ca; }
.st-key-activity-calendar > div { gap: 0 !important; }
.st-key-activity-calendar [data-testid="stHorizontalBlock"] { min-width: 0; flex-wrap: nowrap !important; gap: 0 !important; align-items: stretch; }
.st-key-activity-calendar [data-testid="stColumn"] { width: 14.2857% !important; min-width: 0 !important; max-width: none !important; flex: 1 1 0 !important; }
.st-key-activity-calendar [data-testid="stVerticalBlock"] { gap: .2rem; }
.st-key-activity-calendar [class*="st-key-calendar-day-"] { min-height: 88px; height: 100%; border: 0; border-right: 1px solid #c6d2ca; border-bottom: 1px solid #c6d2ca; border-radius: 0 !important; padding: .35rem; box-sizing: border-box; }
.st-key-activity-calendar [class*="st-key-calendar-day-"] > div { border-radius: 0 !important; }
.st-key-activity-calendar [class*="st-key-calendar-day-"][class*="-saturday"] { background: #f0f6ff; }
.st-key-activity-calendar [class*="st-key-calendar-day-"][class*="-sunday"],
.st-key-activity-calendar [class*="st-key-calendar-day-"][class*="-holiday"] { background: #fff2f2; }
.st-key-activity-calendar [class*="st-key-calendar-day-"][class*="-outside"] { background: #f6f7f6; }
.st-key-activity-calendar [class*="st-key-calendar-day-"][class*="-today"] { box-shadow: inset 0 0 0 2px #14532d; }
.calendar-weekday { text-align: center; font-weight: 600; background: #f4f7f5; padding: .35rem 0; border-right: 1px solid #c6d2ca; border-bottom: 1px solid #c6d2ca; }
.calendar-date { color: #24352c; font-size: .85rem; font-weight: 600; line-height: 1.25; }
.calendar-blue { color: #225ca2; }
.calendar-red { color: #b32632; }
.st-key-activity-calendar .stButton button { background: #e8f5ec; color: #195b33; border: 0; border-left: 2px solid #14532d; border-radius: 0; min-height: 28px; padding: .2rem; }
.st-key-activity-calendar .stButton button:hover { background: #d7eddf; }
.st-key-activity-calendar .stButton button p { font-size: clamp(.65rem, 1vw, .82rem); line-height: 1.25; overflow-wrap: anywhere; }
.st-key-activity-calendar [data-testid="stCaptionContainer"] p { font-size: .68rem; line-height: 1.2; margin: 0; overflow-wrap: anywhere; }
.calendar-event-time { color: #526158; font-size: .68rem; line-height: 1.2; }
.calendar-event-time .mobile-time { display: none; }
[class*="st-key-event-online-"] .stButton button { background: #f0ebfa; color: #624b82; border-left-color: #b9a5d8; }
[class*="st-key-event-offline-"] .stButton button { background: #d6c5eb; color: #45305e; border-left-color: #8566ac; }
[class*="st-key-event-other-"] .stButton button { background: #eef0f2; color: #4c535c; border-left-color: #a4aab2; }
[class*="st-key-event-session-"] .stButton button { background: #e8f3eb; color: #315b40; border-left-color: #8caf98; }
[class*="st-key-event-"] .stButton button:hover { filter: brightness(.96); }
.st-key-activity-calendar [class*="st-key-calendar-day-"][class*="-saturday"] { background: #f0f6ff; }
[class*="st-key-notice-"] { background: #f0f7f1; border-left: 3px solid #91af98; padding: .6rem .8rem; }
.st-key-month-nav [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .35rem !important; }
.st-key-month-nav [data-testid="stColumn"] { min-width: 0 !important; width: 33.333% !important; flex: 1 1 0 !important; }
.st-key-month-nav .stButton button { min-height: 34px; padding: .2rem .4rem; }
.st-key-month-nav .stButton button p { font-size: .8rem; white-space: nowrap; }
@media (max-width: 900px) {
    .st-key-calendar-layout > [data-testid="stHorizontalBlock"] { flex-direction: column; }
    .st-key-calendar-layout > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { width: 100% !important; flex: 1 1 auto !important; }
}
/* PC・スマホ共通：標準ツールバーを隠し、サイドバーの開閉操作を残す。 */
[data-testid="stToolbar"], [data-testid="stAppToolbar"],
[data-testid="stAppDeployButton"], #MainMenu,
[data-testid="stAppViewerBadge"], [class*="viewerBadge"],
[class*="ViewerBadge"], footer { display: none !important; }
/* 閉じたメニューを戻すボタンは、Streamlitのツールバー内にある。 */
[data-testid="stToolbar"]:has([data-testid="stExpandSidebarButton"]),
[data-testid="stAppToolbar"]:has([data-testid="stExpandSidebarButton"]) {
    display: flex !important;
}
[data-testid="stToolbar"] > div > div:not(:has([data-testid="stExpandSidebarButton"])) {
    display: none !important;
}
[data-testid="stExpandSidebarButton"] {
    display: inline-flex !important; visibility: visible !important;
}
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] button {
    width: 48px !important; height: 48px !important;
    min-width: 48px !important; min-height: 48px !important;
    background: #e8f5ec !important; color: #14532d !important;
    border: 1px solid #bdcfc2 !important; border-radius: 10px !important;
}
[data-testid="stExpandSidebarButton"] span,
[data-testid="stSidebarCollapseButton"] button span {
    font-size: 30px !important; color: #14532d !important;
}
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stSidebarCollapseButton"] button:hover {
    background: #d7eddf !important; border-color: #14532d !important;
}
[data-testid="stExpandSidebarButton"]:focus-visible,
[data-testid="stSidebarCollapseButton"] button:focus-visible {
    outline: 3px solid #14532d !important; outline-offset: 2px;
}
[data-testid="stStatusWidget"], [data-testid="stMainMenu"],
[data-testid="stGithubIcon"], [data-testid="stGitHubIcon"],
[data-testid="stHostedAppBadge"], [class*="_viewerBadge"],
.stApp a[href^="https://github.com/"][target="_blank"]:has(svg) { display: none !important; }
.st-key-shift_answers [data-testid="stExpander"] { border-radius: 6px; }
.st-key-activity-detail-heading {
    background: #f0f7f2; border-left: 4px solid #14532d;
    padding: .8rem 1rem; border-radius: 8px;
}
.st-key-activity-detail-heading h3 { font-size: 1.35rem !important; margin: 0; padding: 0; }
.st-key-activity-detail-heading [data-testid="stCaptionContainer"] p { font-size: .85rem; }
.st-key-activity-detail-people, .st-key-activity-detail-memo {
    padding: .8rem 1rem; border: 1px solid #dce9e1; border-radius: 8px;
}
.st-key-activity-detail-people h3, .st-key-activity-detail-memo h3 {
    margin: 0; padding: 0; font-size: 1rem !important;
}
.st-key-activity-detail-people [data-testid="stText"],
.st-key-activity-detail-memo [data-testid="stText"] {
    white-space: pre-wrap; overflow-wrap: anywhere; font-family: inherit; line-height: 1.7;
}
.st-key-activity-detail-memo [data-testid="stForm"] { padding: 0; border: 0; box-shadow: none; }
[class*="st-key-shift-event-session-"] { --shift-color: #e8f3eb; --shift-border: #8caf98; }
[class*="st-key-shift-event-online-"] { --shift-color: #f0ebfa; --shift-border: #b9a5d8; }
[class*="st-key-shift-event-offline-"] { --shift-color: #d6c5eb; --shift-border: #8566ac; }
[class*="st-key-shift-event-other-"] { --shift-color: #eef0f2; --shift-border: #a4aab2; }
[class*="st-key-shift-event-"] [data-testid="stExpander"] { border-left: 4px solid var(--shift-border); }
[class*="st-key-shift-event-"] [data-testid="stExpander"] summary { background: var(--shift-color); border-radius: 4px; }
.st-key-shift_answers [data-testid="stVerticalBlock"] { gap: .5rem; }
.st-key-shift_answers [class*="st-key-shift-parts-"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .5rem !important; }
.st-key-shift_answers [class*="st-key-shift-parts-"] [data-testid="stColumn"] { min-width: 0 !important; width: 50% !important; flex: 1 1 0 !important; }
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] { padding-top: 1.5rem; }
    .spark-welcome { padding: 1.3rem; }
    h1 { font-size: 1.6rem !important; }
    [data-testid="stForm"] { padding: 1rem; }
    .st-key-page [role="radiogroup"] > label { padding: .65rem .75rem; }
    .st-key-activity-calendar [class*="st-key-calendar-day-"] { min-height: 68px; padding: .2rem; }
    .st-key-activity-calendar [data-testid="stCaptionContainer"] p { font-size: .6rem; }
    .st-key-activity-calendar .calendar-date { font-size: .75rem; }
    .st-key-activity-calendar .stButton button { min-height: 36px; padding: .2rem .1rem; }
    .st-key-activity-calendar .stButton button p {
        font-size: .7rem; line-height: 1.3; display: -webkit-box;
        -webkit-box-orient: vertical; -webkit-line-clamp: 2;
        overflow: hidden; max-height: 2.6em; text-align: left;
    }
    .calendar-event-time { font-size: .65rem; white-space: nowrap; }
    .calendar-event-time .desktop-time { display: none; }
    .calendar-event-time .mobile-time { display: inline; }
}
</style>
""", unsafe_allow_html=True)

CSV_SCHEDULE = 'schedule_data.csv'
CSV_DATES = 'target_dates.csv'
CSV_MEMBERS = 'members_data.csv'
CSV_MONTH_DEADLINES = 'monthly_deadlines.csv'
ROOM_DB = 'room_reservations.sqlite3'

# 統括管理者のログイン情報（メールアドレス欄に「統括」と入力）
SUPER_ADMIN_NAME = "統括"
# secrets.tomlファイルがなくてもエラーで止まらないように安全に取得
try:
    SUPER_ADMIN_PASS = st.secrets["SUPER_ADMIN_PASS"]
except Exception:
    SUPER_ADMIN_PASS = None

ROLES = ["選択しない", "① 企画", "② 広報", "③ 人材", "④ システム・サポート", "⑤ 運営・学生サポート", "⑥ 会計"]
GRADES = ["1回生", "2回生", "3回生", "4回生", "大学院生", "その他"]

KANSAI_UNI_HIERARCHY = {
    "選択してください": {"選択してください": []},
    "法学部": {"法学政治学科": []},
    "文学部": {"総合人文学科": ["英米文学英語学専修", "英米文化専修", "国語国文学専修", "哲学専修", "ヨーロッパ文化専修", "日本史・文化遺産学専修", "世界史・地理学専修", "教育文化専修", "初等教育学専修", "心理学専修", "表象文化専修", "アジア文化専修"]},
    "経済学部": {"経済学科": []},
    "商学部": {"商学科": ["流通専修", "ファイナンス専修", "国際ビジネス専修", "マネジメント専修", "会計専修"]},
    "社会学部": {"社会学科": ["社会学専攻", "心理学専攻", "メディア専攻", "社会システムデザイン専攻"]},
    "政策創造学部": {"政策学科": ["政治経済専修", "地域経営専修"], "国際アジア学科": []},
    "外国語学部": {"外国語学科": []},
    "人間健康学部": {"人間健康学科": []},
    "総合情報学部": {"総合情報学科": []},
    "社会安全学部": {"安全マネジメント学科": []},
    "ビジネスデータサイエンス学部": {"ビジネスデータサイエンス学科": []},
    "システム理工学部": {
        "数学科": [],
        "物理・応用物理学科": ["基礎・計算物理コース", "応用物理コース"],
        "機械工学科": ["機械サイエンスコース", "機械フロンティアコース"],
        "電気電子情報工学科": ["電気電子工学コース", "情報通信工学コース", "応用情報工学コース"],
        "グリーンエレクトロニクス工学科": []
    },
    "環境都市工学部": {
        "建築学科": [],
        "都市システム工学科": [],
        "エネルギー環境・化学工学科": []
    },
    "化学生命工学部": {
        "化学・物質工学科": ["マテリアル科学コース", "応用化学コース", "バイオ分子化学コース"],
        "生命・生物工学科": ["ライフサイエンスコース", "バイオテクノロジーコース"]
    },
    "大学院": {"選択してください": []},
    "その他（他大学など）": {"その他": []}
}

# --- セッションステートの初期化 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.is_host = False
    st.session_state.is_super = False
    st.session_state.must_change_password = False
if "notification_text" not in st.session_state:
    st.session_state.notification_text = ""

# --- 補助関数 ---
def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', str(password).encode('utf-8'), salt, 600000)
    return f"pbkdf2_sha256$600000${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    stored = str(stored)
    if len(str(password)) > 1024:
        return False
    if re.fullmatch(r'[a-fA-F0-9]{64}', stored):
        return hmac.compare_digest(hashlib.sha256(str(password).encode('utf-8')).hexdigest(), stored.lower())
    try:
        algorithm, iterations, salt, digest = stored.split('$')
        count = int(iterations)
        if algorithm != 'pbkdf2_sha256' or not 600000 <= count <= 2000000 or len(salt) != 32 or len(digest) != 64:
            return False
        actual = hashlib.pbkdf2_hmac('sha256', str(password).encode('utf-8'), bytes.fromhex(salt), count).hex()
        return hmac.compare_digest(actual, digest)
    except (ValueError, TypeError):
        return False


def credential_fingerprint(value):
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()


def session_is_current():
    if not st.session_state.get('logged_in'):
        return False
    if st.session_state.get('is_super'):
        credential = SUPER_ADMIN_PASS
    else:
        members = load_csv(CSV_MEMBERS)
        active = members[members['メールアドレス'].apply(normalize_email) == normalize_email(st.session_state.get('user_email', ''))]
        credential = active.iloc[-1].get('パスワードハッシュ', '') if not active.empty else None
    return (credential is not None
            and st.session_state.get('auth_fingerprint') == credential_fingerprint(credential)
            and clock_time.time() - st.session_state.get('authenticated_at', 0) <= 8 * 3600)


def save_csv(df, filename):
    """読者が途中まで書かれたCSVを見ることを防ぐ。更新競合は別途トランザクションが必要。"""
    destination = Path(filename).resolve()
    handle, temporary = tempfile.mkstemp(prefix='.csv-write-', suffix='.tmp', dir=destination.parent)
    try:
        with os.fdopen(handle, 'w', encoding='utf-8', newline='') as stream:
            df.to_csv(stream, index=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def normalize_email(email):
    """メールアドレスの大文字小文字を統一し、空白を削除する"""
    return str(email).strip().lower()


def university_email(value, allow_admin=False):
    value = normalize_email(value)
    if allow_admin and value == normalize_email(SUPER_ADMIN_NAME):
        return value
    if not value:
        return ""
    if "@" not in value:
        value += "@kansai-u.ac.jp"
    return value if re.fullmatch(r"[^@\s]+@kansai-u\.ac\.jp", value) else None


def info_message(message):
    key = hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]
    with st.container(key=f"notice-{key}"):
        st.markdown(message)

def parse_bool(val):
    """文字列の'False'がTrueにならないように安全にbool変換する"""
    if isinstance(val, bool):
        return val
    return str(val).lower() in ['true', '1', 't', 'y', 'yes']

def init_files():
    if not os.path.exists(CSV_DATES):
        pd.DataFrame(columns=['日程']).to_csv(CSV_DATES, index=False)
    if not os.path.exists(CSV_MEMBERS):
        pd.DataFrame(columns=[
            '更新日時', '名前', 'メールアドレス', 'パスワードハッシュ', '初回パスワード変更済み', 'ホスト権限', 
            'ふりがな', '役職', '学部', '学科', '専攻', '学年', '居住地(最寄り等)', '補足情報'
        ]).to_csv(CSV_MEMBERS, index=False)

init_files()

def load_csv(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename, dtype=object)
        # 既存CSVの互換性維持（足りない列を補填）
        if filename == CSV_MEMBERS:
            required_cols = ['メールアドレス', 'パスワードハッシュ', '初回パスワード変更済み', '専攻', '先生モード']
            for col in required_cols:
                if col not in df.columns:
                    if col == '先生モード':
                        df[col] = False
                    elif col == '初回パスワード変更済み':
                        df[col] = True # 古いデータは一旦True扱い（ログインできなくなるのを防ぐため）
                    else:
                        df[col] = ""
        return df
    return pd.DataFrame()

ANSWER_OPTIONS = ["未回答", "〇 (参加)", "× (欠席)", "△ (未定)"]


def today_japan():
    return datetime.now(timezone(timedelta(hours=9))).date()


def read_date(value):
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def activity_rows():
    df = load_csv(CSV_DATES)
    monthly = load_csv(CSV_MONTH_DEADLINES)
    deadlines = dict(zip(monthly["対象月"], monthly["回答期限"])) if not monthly.empty else {}
    rows = []
    for record in df.to_dict("records"):
        label = record.get("日程")
        if pd.isna(label) or not str(label).strip():
            continue
        label = str(label)
        day = read_date(record.get("活動日"))
        # 古い日程には年がないため、現在の年を補って未来の予定にしない。
        match = re.search(r"(\d+)月(\d+)日.*?(\d{2}:\d{2})", label)
        legacy_order = (int(match[1]), int(match[2]), match[3]) if match else (13, 32, "")
        memo = record.get("共有メモ", "")
        collect = record.get("参加可否を募る")
        requires_response = True if collect is None or pd.isna(collect) else parse_bool(collect)
        kind = record.get("イベント種類", "")
        if pd.isna(kind) or not str(kind).strip():
            title = activity_title(label)
            kind = title if title in ["セッション", "オンライン会議", "オフライン会議"] else "その他（自由記述）"
        rows.append({"label": label, "day": day, "memo": "" if pd.isna(memo) else str(memo),
                     "kind": kind, "requires_response": requires_response,
                     "room_enabled": parse_bool(record.get("合同研究室利用希望", False)),
                     "deadline": read_date(deadlines.get(day.strftime("%Y-%m"), record.get("回答期限")))
                     if day and requires_response else read_date(record.get("回答期限")), "order": legacy_order})
    return sorted(rows, key=lambda r: (r["day"] is None, r["day"] or date.max, r["order"]))


def my_answers():
    df = load_csv(CSV_SCHEDULE)
    if df.empty or "名前" not in df.columns:
        return {}
    mine = df[df["名前"] == st.session_state.user_name]
    return mine.iloc[-1].to_dict() if not mine.empty else {}


def answer_for(answers, label):
    value = answers.get(label)
    return value if value in ANSWER_OPTIONS else "未回答"


SESSION_PARTS = [("前半", "13:30〜14:30"), ("後半", "14:30〜15:30")]


def part_column(label, part):
    return f"{label}｜{part}"


def aggregate_parts(values):
    for answer in ["未回答", "〇 (参加)", "△ (未定)"]:
        if answer in values:
            return answer
    return "× (欠席)"


def activity_pending(row, answers):
    if not row.get("requires_response", True):
        return False
    if row.get("kind") == "セッション":
        return any(answer_for(answers, part_column(row["label"], part)) == "未回答"
                   for part, _ in SESSION_PARTS)
    return answer_for(answers, row["label"]) == "未回答"


def show_saved_shifts(activities, answers):
    found = False
    for row in activities:
        if not row.get("requires_response", True):
            continue
        label = row["label"]
        columns = [label] + [part_column(label, part) for part, _ in SESSION_PARTS]
        comment = answers.get(f"{label}｜コメント", "")
        comment = "" if pd.isna(comment) else str(comment)
        if not any(answer_for(answers, column) != "未回答" for column in columns) and not comment:
            continue
        found = True
        day = row["day"].strftime("%Y/%m/%d") if row["day"] else "日付確認中"
        identifier = hashlib.sha256(label.encode()).hexdigest()[:16]
        with st.container(key=f"shift-event-{event_tone(row)}-review-{identifier}"):
            with st.expander(f"{day}　{activity_title(label)}"):
                if row.get("kind") == "セッション" and any(part_column(label, part) in answers for part, _ in SESSION_PARTS):
                    for part, hours in SESSION_PARTS:
                        st.write(f"{part}（{hours}）：{answer_for(answers, part_column(label, part))}")
                else:
                    st.caption(activity_time(label))
                    st.write(f"出欠：{answer_for(answers, label)}")
                if comment:
                    st.text(f"コメント：{comment}")
                if room_eligible(row) and room_wanted(label, st.session_state.user_email):
                    show_room_summary(row, room_candidates(row, load_csv(CSV_MEMBERS), load_csv(CSV_SCHEDULE), room_wishes(label)), room_config(label))
    if not found:
        info_message("提出済みのシフトはありません。")


def show_activity(row, answers=None):
    details = [f"活動日：{row['day'].isoformat()}" if row["day"] else "活動年未登録（運営に確認してください）"]
    if row["deadline"]:
        details.append(f"回答期限：{row['deadline'].isoformat()}" + ("（期限経過）" if row["deadline"] < today_japan() else ""))
    else:
        details.append("回答期限：未設定")
    if answers is not None:
        answer = (aggregate_parts([answer_for(answers, part_column(row["label"], part))
                                  for part, _ in SESSION_PARTS]) if row.get("kind") == "セッション"
                  else answer_for(answers, row["label"]))
        details.append("未回答" if answer == "未回答" else f"回答済み：{answer}")
    with st.container(border=True):
        st.write(activity_title(row["label"]))
        st.caption(activity_time(row["label"]))
        st.caption(" ｜ ".join(details))


def go_to_shift():
    st.session_state.page = "📅 シフト"


def go_to_profile():
    st.session_state.page = "👤 マイページ"


def profile_missing_fields(member):
    missing = []
    for field in ["ふりがな", "役職", "学年", "学部", "学科"]:
        value = member.get(field, "")
        if field == "学科" and member.get("学部") == "大学院":
            continue
        if pd.isna(value) or not str(value).strip() or str(value) == "選択してください":
            missing.append(field)
    return missing


def event_tone(row):
    palette = {"セッション": "session", "オンライン会議": "online", "オフライン会議": "offline"}
    return palette.get(row.get("kind"), "other")


def event_button(row, prefix):
    tone = event_tone(row)
    identifier = hashlib.sha256(row["label"].encode("utf-8")).hexdigest()[:16]
    with st.container(key=f"event-{tone}-{prefix}-{identifier}"):
        if st.button(activity_title(row["label"]), key=f"{prefix}-event-{row['label']}",
                     help="参加予定者・共有メモを見る", width="stretch"):
            st.session_state.selected_activity = row["label"]
        event_time = activity_time(row["label"])
        if prefix == "calendar":
            short_time = event_time.split("〜")[0] if "〜" in event_time else "未定"
            st.markdown(f'<div class="calendar-event-time"><span class="desktop-time">{event_time}</span>'
                        f'<span class="mobile-time">{short_time}</span></div>', unsafe_allow_html=True)
        else:
            st.caption(event_time)


def change_calendar_month(offset):
    st.session_state.pop("selected_activity", None)
    month = st.session_state.calendar_month
    index = (month.year - 1) * 12 + month.month - 1 + offset
    if 0 <= index < 9999 * 12:
        st.session_state.calendar_month = date(index // 12 + 1, index % 12 + 1, 1)


def activity_title(label):
    title = re.match(r"【(.*?)】", label)
    if title:
        return title[1]
    return re.sub(r"\s*\d+月\d+日.*$", "", label).strip() or "活動"


def activity_time(label):
    times = re.search(r"(\d{1,2}:\d{2})\s*[-〜～–]\s*(\d{1,2}:\d{2})", label)
    return f"{times[1]}〜{times[2]}" if times else "時間未登録"


def can_edit_activity_memo():
    if not session_is_current():
        return False
    if st.session_state.get("is_super"):
        return True
    if not st.session_state.get("is_host"):
        return False
    members = load_csv(CSV_MEMBERS)
    matches = members[members["メールアドレス"].apply(normalize_email) == normalize_email(st.session_state.get("user_email", ""))]
    return not matches.empty and parse_bool(matches.iloc[-1].get("ホスト権限", False))


def save_activity_memo(label, memo):
    if not can_edit_activity_memo():
        raise PermissionError("共有メモを編集できるのはホスト・統括管理者だけです。")
    df = load_csv(CSV_DATES)
    mask = df["日程"] == label
    if not mask.any():
        return False
    if "共有メモ" not in df.columns:
        df["共有メモ"] = ""
    df.loc[mask, "共有メモ"] = memo
    save_csv(df, CSV_DATES)
    return True


@contextmanager
def room_connection():
    connection = sqlite3.connect(ROOM_DB, timeout=15)
    connection.execute("CREATE TABLE IF NOT EXISTS settings (event TEXT PRIMARY KEY, config TEXT NOT NULL)")
    connection.execute("CREATE TABLE IF NOT EXISTS wishes (event TEXT, email TEXT, wanted INTEGER NOT NULL, PRIMARY KEY(event,email))")
    connection.execute("CREATE TABLE IF NOT EXISTS participation_reviews (email TEXT PRIMARY KEY, config TEXT NOT NULL)")
    connection.commit()
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def room_config(label):
    with room_connection() as connection:
        result = connection.execute("SELECT config FROM settings WHERE event=?", (label,)).fetchone()
    return json.loads(result[0]) if result else {"status": "許可待ち", "capacity": 2, "choices": {}}


def room_wishes(label):
    with room_connection() as connection:
        return {email for email, in connection.execute("SELECT email FROM wishes WHERE event=? AND wanted=1", (label,))}


def room_wanted(label, email):
    return normalize_email(email) in room_wishes(label)


def room_eligible(row):
    return row.get("requires_response", True) and parse_bool(row.get("room_enabled", False))


def can_manage_room():
    if not session_is_current():
        return False
    if st.session_state.get("is_super"):
        return True
    members = load_csv(CSV_MEMBERS)
    current = members[members["メールアドレス"].apply(normalize_email) == normalize_email(st.session_state.get("user_email", ""))]
    return not current.empty and parse_bool(current.iloc[-1].get("先生モード", False))


def room_candidates(row, members, schedule, wishes):
    slots = [part for part, _ in SESSION_PARTS] if row.get("kind") == "セッション" else ["全時間"]
    result = {slot: {} for slot in slots}
    if schedule.empty or members.empty:
        return result
    latest = schedule.drop_duplicates("名前", keep="last").set_index("名前")
    for member in members.drop_duplicates("メールアドレス", keep="last").to_dict("records"):
        email = normalize_email(member["メールアドレス"])
        name = member["名前"]
        if email not in wishes or name not in latest.index:
            continue
        answers = latest.loc[name].to_dict()
        for slot in slots:
            column = part_column(row["label"], slot) if slot != "全時間" else row["label"]
            if answer_for(answers, column) == "〇 (参加)":
                result[slot][email] = str(name)
    return result


def room_results(candidates, config):
    result = {}
    for slot, people in candidates.items():
        chosen = config.get("choices", {}).get(slot, {})
        if config["status"] == "利用不可":
            state, confirmed = "利用不可", []
        elif config["status"] != "利用可":
            state, confirmed = "先生の許可待ち（未確定）", []
        elif len(people) <= config["capacity"]:
            state, confirmed = "利用確定", list(people)
        elif (chosen.get("candidates") == sorted(people)
              and 0 < len(chosen.get("selected", [])) <= config["capacity"]
              and set(chosen["selected"]).issubset(people)):
            state, confirmed = "利用者の選定済み", chosen["selected"]
        else:
            state, confirmed = "管理者による調整待ち（未確定）", []
        result[slot] = {"state": state, "confirmed": confirmed, "people": people}
    return result


def save_room_wishes(edits):
    if not session_is_current() or st.session_state.get("is_super"):
        raise PermissionError("メンバー本人だけが利用希望を保存できます。")
    members = load_csv(CSV_MEMBERS)
    email = normalize_email(st.session_state.user_email)
    if not members["メールアドレス"].apply(normalize_email).eq(email).any():
        raise PermissionError("登録されているメンバーだけが利用希望を保存できます。")
    eligible = {r["label"] for r in activity_rows() if room_eligible(r)}
    with room_connection() as connection:
        for label, wanted in edits.items():
            if label in eligible:
                connection.execute("INSERT OR REPLACE INTO wishes VALUES (?,?,?)", (label, email, int(wanted)))


def save_room_config(label, config, expected, expected_config=None):
    if not can_manage_room():
        raise PermissionError("研究室を管理できるのは統括管理者と先生モードだけです。")
    row = next((r for r in activity_rows() if r["label"] == label and room_eligible(r)), None)
    if row is None:
        raise ValueError("この予定は研究室予約の対象ではありません。")
    fresh = room_candidates(row, load_csv(CSV_MEMBERS), load_csv(CSV_SCHEDULE), room_wishes(label))
    if fresh != expected:
        raise ValueError("利用希望が変更されました。画面を更新して選び直してください。")
    if config["status"] not in ["許可待ち", "利用可", "利用不可"] or config["capacity"] not in [1, 2, 3, 4]:
        raise ValueError("利用可否・定員を確認してください。")
    for slot, choice in config["choices"].items():
        if len(choice["selected"]) > config["capacity"] or not set(choice["selected"]).issubset(fresh.get(slot, {})):
            raise ValueError("定員以内で利用希望者を選んでください。")
    with room_connection() as connection:
        connection.execute('BEGIN IMMEDIATE')
        stored = connection.execute('SELECT config FROM settings WHERE event=?', (label,)).fetchone()
        current_config = json.loads(stored[0]) if stored else {'status': '許可待ち', 'capacity': 2, 'choices': {}}
        if expected_config is not None and current_config != expected_config:
            raise ValueError('他の管理者が研究室の設定を変更しました。画面を更新してください。')
        connection.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (label, json.dumps(config, ensure_ascii=False)))


def show_room_summary(row, candidates, config):
    with st.container(border=True):
        st.subheader("池澤先生の合同研究室")
        if config["status"] == "許可待ち":
            st.warning("利用希望受付中・先生の許可待ち（予約未確定）")
        elif config["status"] == "利用可":
            st.success(f"利用できます · 各時間帯 {config['capacity']}名まで")
        else:
            st.error("この日は利用できません")
        for slot, result in room_results(candidates, config).items():
            st.write(f"**{slot}** · 希望 {len(result['people'])}名 / 定員 {config['capacity']}名")
            st.caption(result["state"])
            if result["confirmed"]:
                st.text("確定：" + "、".join(result["people"][email] for email in result["confirmed"]))
            own = normalize_email(st.session_state.get("user_email", ""))
            if own in result["people"]:
                state = "利用確定" if own in result["confirmed"] else ("今回は選定されていません" if result["state"] == "利用者の選定済み" else result["state"])
                st.write(f"あなた：{state}")


def show_room_manager(row, demo=False):
    if not can_manage_room():
        st.error("統括管理者と先生モードだけが利用できます。")
        return
    prefix = "room_demo" if demo else "room_live"
    if demo:
        st.warning("デモ：架空のメンバーを使用します。本番データには保存しません。")
        candidates = {"前半": {}, "後半": {}}
        for index, name in enumerate(["学生A", "学生B", "学生C"]):
            selection = st.selectbox(f"{name}の利用希望", ["前半・後半", "前半のみ", "後半のみ", "希望なし"], key=f"demo_person_{index}")
            for slot in candidates:
                if selection == "前半・後半" or selection == f"{slot}のみ":
                    candidates[slot][f"demo{index}"] = name
        config = st.session_state.get("room_demo_config", {"status": "許可待ち", "capacity": 2, "choices": {}})
    else:
        config = room_config(row["label"])
        candidates = room_candidates(row, load_csv(CSV_MEMBERS), load_csv(CSV_SCHEDULE), room_wishes(row["label"]))
    show_room_summary(row, candidates, config)
    identity = hashlib.sha256(json.dumps([row["label"], config, candidates], sort_keys=True).encode()).hexdigest()[:12]
    with st.form(f"{prefix}_{identity}"):
        status = st.selectbox("研究室の利用可否", ["許可待ち", "利用可", "利用不可"], index=["許可待ち", "利用可", "利用不可"].index(config["status"]))
        capacity = st.selectbox("各時間帯の定員", [1, 2, 3, 4], index=config["capacity"] - 1)
        choices = {}
        st.caption("定員内なら自動確定します。定員超過時は、各時間帯の利用者を選んで保存してください。")
        for slot, people in candidates.items():
            old = config.get("choices", {}).get(slot, {})
            defaults = old.get("selected", []) if old.get("candidates") == sorted(people) else []
            selected = st.multiselect(f"{slot}の利用者（定員超過時）", list(people), default=defaults,
                                      format_func=lambda email, people=people: people[email] if demo else f"{people[email]} ({email})", key=f"{prefix}_{identity}_{slot}")
            choices[slot] = {"candidates": sorted(people), "selected": selected}
        saved = st.form_submit_button("デモに反映" if demo else "利用可否・利用者を保存", type="primary")
    if saved:
        new = {"status": status, "capacity": capacity, "choices": choices}
        if any(len(choice["selected"]) > capacity for choice in choices.values()):
            st.error("各時間帯の定員以内で選んでください。")
        else:
            try:
                if demo:
                    st.session_state.room_demo_config = new
                else:
                    save_room_config(row["label"], new, candidates, expected_config=config)
                st.rerun()
            except (PermissionError, ValueError) as error:
                st.error(str(error))
    if demo and st.button("デモを最初に戻す"):
        for key in list(st.session_state):
            if key.startswith("room_demo") or key.startswith("demo_person_"):
                del st.session_state[key]
        st.rerun()


def activity_record_version(record):
    clean = {key: '' if pd.isna(value) else str(value) for key, value in record.items()}
    return hashlib.sha256(json.dumps(clean, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def edit_activity(old_label, changes, expected_version):
    if not can_edit_activity_memo():
        raise PermissionError("日程を変更できるのはホストと統括管理者だけです。")
    dates = load_csv(CSV_DATES)
    matches = dates.index[dates['日程'] == old_label]
    if len(matches) != 1 or activity_record_version(dates.loc[matches[0]].to_dict()) != expected_version:
        raise ValueError("日程が変更されたか削除されています。画面を更新してください。")
    new_label = changes['日程']
    if new_label != old_label and dates['日程'].eq(new_label).any():
        raise ValueError("同じ日程が既に登録されています。")
    schedule = load_csv(CSV_SCHEDULE)
    renames = {column: new_label + column[len(old_label):] for column in schedule.columns
               if column == old_label or column.startswith(old_label + '｜')}
    if new_label != old_label and any(value in schedule.columns and value not in renames for value in renames.values()):
        raise ValueError("変更先に既存の回答があります。別の日程を指定してください。")
    updated_dates = dates.copy()
    for column, value in changes.items():
        updated_dates.loc[matches[0], column] = value
    updated_schedule = schedule.rename(columns=renames)
    with room_connection() as connection:
        connection.execute('BEGIN IMMEDIATE')
        if new_label != old_label:
            if connection.execute('SELECT 1 FROM settings WHERE event=? UNION SELECT 1 FROM wishes WHERE event=?', (new_label, new_label)).fetchone():
                raise ValueError("変更先に研究室の予約データがあります。別の日程を指定してください。")
            connection.execute('UPDATE settings SET event=? WHERE event=?', (new_label, old_label))
            connection.execute('UPDATE wishes SET event=? WHERE event=?', (new_label, old_label))
        try:
            save_csv(updated_dates, CSV_DATES)
            if not schedule.empty or os.path.exists(CSV_SCHEDULE):
                save_csv(updated_schedule, CSV_SCHEDULE)
        except Exception:
            save_csv(dates, CSV_DATES)
            if os.path.exists(CSV_SCHEDULE):
                save_csv(schedule, CSV_SCHEDULE)
            raise


def delete_activities(labels):
    if not can_edit_activity_memo():
        raise PermissionError("日程を削除できるのはホストと統括管理者だけです。")
    dates = load_csv(CSV_DATES)
    selected = set(labels) & set(dates['日程'])
    if not selected:
        raise ValueError("削除する日程を選んでください。")
    schedule = load_csv(CSV_SCHEDULE)
    columns = [column for column in schedule.columns if any(column == label or column.startswith(label + '｜') for label in selected)]
    with room_connection() as connection:
        for label in selected:
            connection.execute('DELETE FROM settings WHERE event=?', (label,))
            connection.execute('DELETE FROM wishes WHERE event=?', (label,))
        save_csv(dates[~dates['日程'].isin(selected)], CSV_DATES)
        if columns:
            save_csv(schedule.drop(columns=columns), CSV_SCHEDULE)
    return len(selected)


def delete_members(emails):
    if not session_is_current() or not st.session_state.get('is_super'):
        raise PermissionError("メンバーを削除できるのは統括管理者だけです。")
    members = load_csv(CSV_MEMBERS)
    selected = members['メールアドレス'].apply(normalize_email).isin({normalize_email(email) for email in emails})
    if not selected.any():
        raise ValueError("削除するメンバーを選んでください。")
    remaining = members[~selected]
    deleted_emails = {normalize_email(email) for email in members.loc[selected, 'メールアドレス']}
    deleted_names = set(members.loc[selected, '名前']) - set(remaining['名前'])
    schedule = load_csv(CSV_SCHEDULE)
    with room_connection() as connection:
        for email in members.loc[selected, 'メールアドレス']:
            connection.execute('DELETE FROM wishes WHERE email=?', (normalize_email(email),))
            connection.execute('DELETE FROM participation_reviews WHERE email=?', (normalize_email(email),))
        for event, raw in connection.execute('SELECT event,config FROM settings').fetchall():
            config = json.loads(raw)
            choices = config.get('choices', {})
            affected = [slot for slot, choice in choices.items()
                        if deleted_emails & set(choice.get('selected', []) + choice.get('candidates', []))]
            for slot in affected:
                del choices[slot]
            if affected:
                connection.execute('UPDATE settings SET config=? WHERE event=?', (json.dumps(config, ensure_ascii=False), event))
        save_csv(remaining, CSV_MEMBERS)
        if not schedule.empty:
            save_csv(schedule[~schedule['名前'].isin(deleted_names)], CSV_SCHEDULE)
    return int(selected.sum())


def require_super():
    if not session_is_current() or not st.session_state.get('is_super'):
        raise PermissionError('統括管理者だけが利用できます。')


def load_participation_reviews():
    require_super()
    with room_connection() as connection:
        return {email: json.loads(raw) for email, raw in connection.execute('SELECT email,config FROM participation_reviews')}


def save_participation_review(email, config):
    require_super()
    email = normalize_email(email)
    members = load_csv(CSV_MEMBERS)
    if email not in members['メールアドレス'].apply(normalize_email).values:
        raise ValueError('メンバーが変更されています。画面を開き直してください。')
    joined = read_date(config.get('registered'))
    until = read_date(config.get('exempt_until'))
    if joined and joined > today_japan():
        raise ValueError('登録日は今日以前にしてください。')
    clean = {'registered': joined.isoformat() if joined else '',
             'exempt_until': until.isoformat() if until else '',
             'note': str(config.get('note', ''))[:1000],
             'updated': datetime.now(timezone(timedelta(hours=9))).isoformat()}
    with room_connection() as connection:
        connection.execute('INSERT OR REPLACE INTO participation_reviews VALUES (?,?)', (email, json.dumps(clean, ensure_ascii=False)))


def participation_report(members, schedule, activities, reviews, today):
    # 更新日時を登録日の代用にしない。対象は完了した直近2暦月。
    end = today.replace(day=1) - timedelta(days=1)
    start = (end.replace(day=1) - timedelta(days=1)).replace(day=1)
    rows = [r for r in activities if r.get('requires_response', True) and r.get('day') and start <= r['day'] <= end]
    undated = any(r.get('requires_response', True) and not r.get('day') for r in activities)
    records = {} if schedule.empty or '名前' not in schedule else schedule.drop_duplicates('名前', keep='last').set_index('名前').to_dict('index')
    duplicates = set(members.loc[members['名前'].duplicated(keep=False), '名前'])
    result = []
    for member in members.to_dict('records'):
        email = normalize_email(member['メールアドレス'])
        review = reviews.get(email, {})
        joined = read_date(review.get('registered')) or read_date(member.get('登録日'))
        exempt = read_date(review.get('exempt_until'))
        answers = records.get(member['名前'], {})
        counts = {'参加希望': 0, '未定': 0, '欠席': 0, '未回答': 0}
        last = None
        for r in activities:
            if not r.get('requires_response', True) or not r.get('day') or r['day'] > end:
                continue
            values = [answer_for(answers, part_column(r['label'], part)) for part, _ in SESSION_PARTS] if r['kind'] == 'セッション' else [answer_for(answers, r['label'])]
            if r['kind'] == 'セッション' and not any(answers.get(part_column(r['label'], part)) in ANSWER_OPTIONS for part, _ in SESSION_PARTS):
                # 前半・後半の導入前に保存された回答も参加意思として扱う。
                values = [answer_for(answers, r['label'])]
            if ANSWER_OPTIONS[1] in values:
                state = '参加希望'
                last = max(last or r['day'], r['day'])
            elif ANSWER_OPTIONS[0] in values:
                state = '未回答'
            elif ANSWER_OPTIONS[3] in values:
                state = '未定'
            else:
                state = '欠席'
            if start <= r['day'] <= end:
                counts[state] += 1
        if exempt and exempt >= today:
            status = '例外期間中'
        elif member['名前'] in duplicates:
            status = '保留：同名メンバー'
        elif not joined:
            status = '保留：登録日不明'
        elif joined > start:
            status = '保留：対象期間の途中で登録'
        elif len({r['day'].strftime('%Y-%m') for r in rows}) < 2:
            status = '保留：対象予定がない月あり'
        elif counts['参加希望']:
            status = '参加希望あり'
        elif undated:
            status = '保留：日付不明の予定あり'
        else:
            status = '要確認：参加希望なし'
        result.append({'名前': member['名前'], '利用者ID': email.split('@')[0], '判定': status,
                       '対象予定': len(rows), **counts, '最終参加希望': last.isoformat() if last else '記録なし',
                       '例外期限': exempt.isoformat() if exempt else ''})
    return start, end, result


def show_participation_review(activities):
    require_super()
    st.subheader('参加意思の確認')
    st.caption('統括管理者のみ。現在保存されているシフト回答を確認します。実際の出欠・期限内の回答を証明するものではありません。面談等の判断は個別に行ってください。')
    members = load_csv(CSV_MEMBERS)
    if members.empty:
        info_message('登録メンバーがいません。')
        return
    reviews = load_participation_reviews()
    start, end, report = participation_report(members, load_csv(CSV_SCHEDULE), activities, reviews, today_japan())
    st.write(f'確認期間：{start:%Y/%m/%d} ～ {end:%Y/%m/%d}')
    st.metric('確認候補', f"{sum(r['判定'].startswith('要確認') for r in report)}名")
    only = st.checkbox('確認候補・判定保留のみ表示', value=True)
    visible = [r for r in report if r['判定'].startswith(('要確認', '保留'))] if only else report
    st.dataframe(pd.DataFrame(visible, columns=list(report[0])), hide_index=True, width='stretch')
    with st.expander('登録日・留学などの例外を記録する'):
        choices = {normalize_email(m['メールアドレス']): m for m in members.to_dict('records')}
        email = st.selectbox('記録するメンバー', list(choices), format_func=lambda e: f"{choices[e]['名前']}（{e.split('@')[0]}）", key='review_member')
        review = reviews.get(email, {})
        registered = read_date(review.get('registered')) or read_date(choices[email].get('登録日'))
        until = read_date(review.get('exempt_until'))
        with st.form('participation_review_' + hashlib.sha256(email.encode()).hexdigest()[:12]):
            known = st.checkbox('登録日を設定する', value=bool(registered))
            st.caption('チェックを外すと管理者の補正を解除し、新規登録時の登録日を使います。旧メンバーで登録日がなければ不明として扱います。')
            joined = st.date_input('登録日', value=registered or today_japan(), min_value=date(1900, 1, 1), max_value=today_japan())
            exempt = st.checkbox('特別な事情による例外期間を設定する', value=bool(until))
            exempt_until = st.date_input('例外期限', value=until or today_japan())
            note = st.text_area('統括管理者用メモ', value=review.get('note', ''), max_chars=1000, help='留学などの理由や面談状況を必要最小限で記録してください。')
            if st.form_submit_button('確認記録を保存'):
                try:
                    save_participation_review(email, {'registered': joined.isoformat() if known else '', 'exempt_until': exempt_until.isoformat() if exempt else '', 'note': note})
                    st.session_state.review_notice = '確認記録を保存しました。'
                    st.rerun()
                except (ValueError, PermissionError) as error:
                    st.error(str(error))
    if st.session_state.get('review_notice'):
        st.success(st.session_state.pop('review_notice'))


def reset_delete_confirmation(key):
    st.session_state[key] = False


def show_activity_editor():
    dates = load_csv(CSV_DATES)
    if dates.empty:
        info_message("編集できる日程がありません。")
        return
    label = st.selectbox("変更する予定", dates['日程'].tolist(), key='edit_event')
    record = dates[dates['日程'] == label].iloc[0].to_dict()
    version = activity_record_version(record)
    row = next(row for row in activity_rows() if row['label'] == label)
    kind_options = ['セッション', 'オンライン会議', 'オフライン会議', 'その他（自由記述）']
    kind = st.selectbox("変更後のイベント種類", kind_options, index=kind_options.index(row['kind']) if row['kind'] in kind_options else 3, key=f'edit_kind_{version}')
    with st.form(f'edit_activity_{version}_{kind}'):
        title = st.text_input("予定の名称", value=activity_title(label), key=f'edit_title_{version}')
        day = st.date_input("変更後の日付", value=row['day'] or today_japan(), min_value=date(1900,1,1), max_value=date(9999,12,31), key=f'edit_day_{version}')
        match = re.search(r'(\d{1,2}:\d{2})\s*[-〜～–]\s*(\d{1,2}:\d{2})', label)
        old_start = time.fromisoformat(match[1]) if match else time(13,30)
        old_end = time.fromisoformat(match[2]) if match else time(15,30)
        start = st.time_input("変更後の開始時間", value=time(13,30) if kind == 'セッション' else old_start, disabled=kind == 'セッション', key=f'edit_start_{version}_{kind}')
        end = st.time_input("変更後の終了時間", value=time(15,30) if kind == 'セッション' else old_end, disabled=kind == 'セッション', key=f'edit_end_{version}_{kind}')
        if kind == 'セッション':
            st.caption("前半13:30〜14:30・後半14:30〜15:30に合わせています。")
        collect = st.checkbox("変更後も参加可否を募る", value=row['requires_response'], key=f'edit_collect_{version}')
        room_enabled = st.checkbox("池澤先生の合同研究室利用希望を追加する", value=row['room_enabled'],
                                   key=f'edit_room_{version}',
                                   help="参加可否を募る予定で利用できます。オフにすると申請欄を非表示にし、保存済みの希望は保持します。")
        original_deadline = read_date(record.get('回答期限'))
        use_deadline = st.checkbox("個別の回答期限を使う", value=original_deadline is not None, key=f'edit_use_deadline_{version}')
        deadline = st.date_input("個別の回答期限", value=original_deadline or today_japan(), min_value=date(1900,1,1), max_value=date(9999,12,31), key=f'edit_deadline_{version}')
        st.caption("回答・コメント・共有メモ・研究室の希望を引き継ぎます。月の期限を設定している場合は、変更後の月の期限が優先されます。")
        submitted = st.form_submit_button("予定の変更を保存", type='primary')
    if submitted:
        if not title.strip() or end <= start or (collect and use_deadline and deadline > day):
            st.error("名称・時間・回答期限を確認してください。")
            return
        weekdays = ['月','火','水','木','金','土','日']
        new_label = f"【{title.strip()}】 {day.year}年{day.month}月{day.day}日({weekdays[day.weekday()]}) {start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
        changes = {'日程': new_label, '活動日': day.isoformat(), 'イベント種類': kind,
                   '参加可否を募る': bool(collect), '合同研究室利用希望': bool(collect and room_enabled),
                   '回答期限': deadline.isoformat() if collect and use_deadline else ''}
        try:
            edit_activity(label, changes, version)
            st.session_state.notification_text = f"予定を変更しました。\n変更前：{label}\n変更後：{new_label}"
            st.session_state.pop('selected_activity', None)
            st.rerun()
        except (PermissionError, ValueError) as error:
            st.error(str(error))


def close_activity_details():
    st.session_state.pop("selected_activity", None)


@st.dialog("予定の詳細", width="large", on_dismiss=close_activity_details)
def show_activity_details(label):
    row = next((r for r in activity_rows() if r["label"] == label), None)
    if row is None:
        info_message("この予定は削除されています。")
        return
    with st.container(key="activity-detail-heading"):
        st.subheader(activity_title(label))
        if row["day"]:
            weekdays = ["月", "火", "水", "木", "金", "土", "日"]
            st.write(f"{row['day'].year}年{row['day'].month}月{row['day'].day}日（{weekdays[row['day'].weekday()]}）")
        else:
            st.write("日付確認中")
        st.caption(activity_time(label))
        if row.get("requires_response", True) and row["deadline"]:
            st.caption(f"回答期限：{row['deadline'].strftime('%Y/%m/%d')} 23:59まで")
            if row["deadline"] < today_japan():
                st.error("回答期限を過ぎています")
    schedule = load_csv(CSV_SCHEDULE)
    names = []
    if not schedule.empty and label in schedule.columns and "名前" in schedule.columns:
        latest = schedule.drop_duplicates("名前", keep="last")
        members = load_csv(CSV_MEMBERS)
        latest = latest[latest["名前"].isin(members["名前"])]
        if row.get("kind") == "セッション":
            for record in latest.to_dict("records"):
                parts = [part for part, _ in SESSION_PARTS
                         if answer_for(record, part_column(label, part)) == "〇 (参加)"]
                if parts and not pd.isna(record.get("名前")):
                    names.append(f"{record['名前']}（{'・'.join(parts)}）")
        else:
            names = latest.loc[latest[label] == "〇 (参加)", "名前"].dropna().astype(str).tolist()
    if not row.get("requires_response", True):
        st.caption("お知らせ（参加可否の回答は不要です）")
    else:
        with st.container(key="activity-detail-people"):
            st.subheader(f"参加予定者（{len(names)}人）")
            if names:
                st.text("\n".join(names))
            else:
                st.caption("まだいません")
    if room_eligible(row):
        show_room_summary(row, room_candidates(row, load_csv(CSV_MEMBERS), load_csv(CSV_SCHEDULE), room_wishes(label)), room_config(label))
    with st.container(key="activity-detail-memo"):
        st.subheader("共有メモ")
        if can_edit_activity_memo():
            with st.form("activity_memo_form"):
                memo = st.text_area("メモ", value=row["memo"], label_visibility="collapsed",
                                    placeholder="集合場所・持ち物など", key=f"memo_{label}", height=100)
                submitted = st.form_submit_button("メモを保存する", type="primary", width="stretch")
            if submitted:
                if save_activity_memo(label, memo):
                    st.success("メモを共有しました。")
                else:
                    st.error("予定が削除されたため保存できませんでした。")
        elif row["memo"]:
            st.text(row["memo"])
        else:
            st.caption("なし")


def show_calendar(month, activities, today):
    holidays = japan_holidays()
    by_day = {}
    for row in activities:
        if row["day"] and (row["day"].year, row["day"].month) == (month.year, month.month):
            by_day.setdefault(row["day"].day, []).append(row)
    st.subheader(f"{month.year}年{month.month}月")
    with st.container(key="activity-calendar"):
        for weekday_index, (column, weekday) in enumerate(zip(st.columns(7, gap=None), ["月", "火", "水", "木", "金", "土", "日"])):
            color = "calendar-blue" if weekday_index == 5 else "calendar-red" if weekday_index == 6 else ""
            column.markdown(f'<div class="calendar-weekday {color}">{weekday}</div>', unsafe_allow_html=True)
        for week_index, week in enumerate(calendar.Calendar().monthdayscalendar(month.year, month.month)):
            for column_index, (column, number) in enumerate(zip(st.columns(7, gap=None), week)):
                day = date(month.year, month.month, number) if number else None
                holiday = day in holidays
                tone = "outside" if not number else "holiday" if holiday else "saturday" if column_index == 5 else "sunday" if column_index == 6 else "weekday"
                today_key = "-today" if day == today else ""
                with column:
                    with st.container(key=f"calendar-day-{week_index}-{column_index}-{tone}{today_key}"):
                        if not number:
                            st.write(" ")
                            continue
                        color = "calendar-red" if holiday or column_index == 6 else "calendar-blue" if column_index == 5 else ""
                        marker = "・祝" if holiday else ""
                        st.markdown(f'<div class="calendar-date {color}">{number}{marker}</div>', unsafe_allow_html=True)
                        for row in by_day.get(number, []):
                            event_button(row, "calendar")


@st.cache_data
def japan_holidays():
    """内閣府の公開CSVに記載された祝日・振替休日を使用する。"""
    path = Path(__file__).with_name("japan_holidays.csv")
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as file:
        records = csv.reader(file)
        next(records, None)
        return {datetime.strptime(record[0], "%Y/%m/%d").date(): record[1]
                for record in records if len(record) >= 2 and record[0].strip()}




# ==========================================
# 2. ログイン画面
# ==========================================
if st.session_state.logged_in:
    if not session_is_current():
        st.session_state.clear()
        st.session_state.login_notice = "認証情報が変更されたか、有効期限が切れました。再度ログインしてください。"
        st.rerun()

if not st.session_state.logged_in:
    if st.session_state.get('login_notice'):
        st.warning(st.session_state.pop('login_notice'))
    st.markdown("""
    <style>
    [data-testid="stMainBlockContainer"] { max-width: 460px; padding: 2rem 1rem 1rem; }
    .spark-welcome { padding: .65rem 1rem; margin-bottom: .5rem; }
    .spark-welcome h1 { font-size: 1.3rem !important; }
    [data-testid="stForm"] { padding: .8rem; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="spark-welcome">
        <div class="spark-brand">J-EXCHANGE SPARK</div>
        <h1>ログイン</h1>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        input_email = st.text_input("利用者ID", placeholder="例：k123456",
                                   help="@kansai-u.ac.jp は自動で補います。統括管理者は「統括」と入力してください。")
        input_pass = st.text_input("パスワード", type="password")
        
        login_btn = st.form_submit_button("ログイン", type="primary", width="stretch")
        
        if login_btn:
            if clock_time.time() < st.session_state.get('login_block_until', 0):
                st.error("ログインの試行が続いたため、30秒ほど待って再度お試しください。")
                st.stop()
            st.session_state.login_failures = st.session_state.get('login_failures', 0) + 1
            if st.session_state.login_failures >= 5:
                st.session_state.login_block_until = clock_time.time() + 30
                st.session_state.login_failures = 0
            if input_email and input_pass:
                norm_email = university_email(input_email, allow_admin=True)
                if norm_email is None:
                    st.error("関西大学のメールアドレスを入力してください。")
                    st.stop()
                
                # ① 統括管理者のログイン判定
                if norm_email == normalize_email(SUPER_ADMIN_NAME) and SUPER_ADMIN_PASS and hmac.compare_digest(input_pass.encode('utf-8'), str(SUPER_ADMIN_PASS).encode('utf-8')):
                    st.session_state.logged_in = True
                    st.session_state.user_name = "統括管理者"
                    st.session_state.user_email = SUPER_ADMIN_NAME
                    st.session_state.is_host = True
                    st.session_state.is_super = True
                    st.session_state.must_change_password = False
                    st.session_state.auth_fingerprint = credential_fingerprint(SUPER_ADMIN_PASS)
                    st.session_state.authenticated_at = clock_time.time()
                    st.session_state.login_failures = 0
                    st.session_state.login_block_until = 0
                    st.rerun()
                else:
                    df_members = load_csv(CSV_MEMBERS)
                    if df_members.empty:
                        st.error("利用者IDまたはパスワードが違います。")
                    else:
                        # メールアドレスでユーザーを検索
                        df_members['検索用メール'] = df_members['メールアドレス'].apply(normalize_email)
                        matched_users = df_members[df_members['検索用メール'] == norm_email]
                        
                        if matched_users.empty:
                            st.error("利用者IDまたはパスワードが違います。")
                        else:
                            user_data = matched_users.iloc[-1]
                            # パスワードのハッシュ照合
                            if verify_password(input_pass, user_data['パスワードハッシュ']):
                                # 認証後の再読込で、途中のリセットを上書きしない。
                                latest_members = load_csv(CSV_MEMBERS)
                                latest_idx = latest_members[latest_members['メールアドレス'].apply(normalize_email) == norm_email].index
                                if latest_idx.empty or str(latest_members.loc[latest_idx[-1], 'パスワードハッシュ']) != str(user_data['パスワードハッシュ']):
                                    st.error("認証情報が変更されました。もう一度ログインしてください。")
                                    st.stop()
                                if not str(user_data['パスワードハッシュ']).startswith('pbkdf2_sha256$'):
                                    new_hash = hash_password(input_pass)
                                    latest_members.loc[latest_idx, 'パスワードハッシュ'] = new_hash
                                    save_csv(latest_members, CSV_MEMBERS)
                                    user_data['パスワードハッシュ'] = new_hash
                                st.session_state.logged_in = True
                                st.session_state.user_name = user_data['名前']
                                st.session_state.user_email = user_data['メールアドレス']
                                st.session_state.is_host = parse_bool(user_data.get('ホスト権限', False))
                                st.session_state.is_super = False
                                st.session_state.auth_fingerprint = credential_fingerprint(user_data['パスワードハッシュ'])
                                st.session_state.authenticated_at = clock_time.time()
                                st.session_state.login_failures = 0
                                st.session_state.login_block_until = 0
                                
                                # 初回ログイン判定
                                if not parse_bool(user_data.get('初回パスワード変更済み', False)):
                                    st.session_state.must_change_password = True
                                else:
                                    st.session_state.must_change_password = False
                                
                                st.rerun()
                            else:
                                st.error("利用者IDまたはパスワードが違います。")
            else:
                st.error("利用者IDとパスワードを入力してください。")

# ==========================================
# 3. 初回パスワード変更画面（強制）
# ==========================================
elif st.session_state.must_change_password:
    st.title("🔐 初回パスワード変更")
    st.warning("セキュリティのため、初期パスワードからの変更が必要です。新しいパスワードを設定してください。")
    
    with st.form("force_password_change_form"):
        new_pass = st.text_input("新しいパスワード", type="password")
        new_pass_confirm = st.text_input("新しいパスワード（確認用）", type="password")
        
        if st.form_submit_button("パスワードを変更してホームへ進む"):
            if not new_pass:
                st.error("新しいパスワードを入力してください。")
            elif new_pass != new_pass_confirm:
                st.error("パスワードが一致しません。")
            elif not 12 <= len(new_pass) <= 128:
                st.error("新しいパスワードは12〜128文字で設定してください。")
            else:
                # パスワードを更新
                df_members = load_csv(CSV_MEMBERS)
                norm_email = normalize_email(st.session_state.user_email)
                df_members['検索用メール'] = df_members['メールアドレス'].apply(normalize_email)
                
                # 対象ユーザーの行を更新
                target_idx = df_members[df_members['検索用メール'] == norm_email].index
                if target_idx.empty or credential_fingerprint(df_members.loc[target_idx[-1], 'パスワードハッシュ']) != st.session_state.auth_fingerprint:
                    st.session_state.clear()
                    st.rerun()
                df_members.loc[target_idx, 'パスワードハッシュ'] = hash_password(new_pass)
                df_members.loc[target_idx, '初回パスワード変更済み'] = True
                df_members.loc[target_idx, '更新日時'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 検索用列を消して保存
                df_members = df_members.drop(columns=['検索用メール'])
                save_csv(df_members, CSV_MEMBERS)
                st.session_state.auth_fingerprint = credential_fingerprint(df_members.loc[target_idx[-1], 'パスワードハッシュ'])
                
                st.session_state.must_change_password = False
                st.success("パスワードを変更しました！")
                st.rerun()
                
    if st.button("ログアウト"):
        st.session_state.logged_in = False
        st.session_state.must_change_password = False
        st.rerun()

# ==========================================
# 4. メイン画面（通常利用）
# ==========================================
else:
    # メニューの表示だけでなく、各再実行時に保存済みの権限を確認する。
    if not st.session_state.is_super:
        members = load_csv(CSV_MEMBERS)
        current = members[members['メールアドレス'].apply(normalize_email) == normalize_email(st.session_state.user_email)]
        if current.empty:
            st.session_state.clear()
            st.rerun()
        current_user = current.iloc[-1]
        st.session_state.is_host = parse_bool(current_user.get('ホスト権限', False))
        st.session_state.user_name = current_user['名前']
        if not parse_bool(current_user.get('初回パスワード変更済み', False)):
            st.session_state.must_change_password = True
            st.rerun()

    activities = activity_rows()
    answers = {} if st.session_state.is_super else my_answers()
    today = today_japan()
    upcoming = [r for r in activities if r["day"] and r["day"] >= today]
    undated = [r for r in activities if r["day"] is None]
    pending = [] if st.session_state.is_super else [
        r for r in upcoming + undated if activity_pending(r, answers)]
    if pending:
        st.markdown("""
        <style>
        .st-key-page [role="radiogroup"] > label:nth-of-type(2) {
            background: #fff0f0; border-left-color: #b42318; color: #b42318;
        }
        .st-key-page [role="radiogroup"] > label:nth-of-type(2) p {
            color: #b42318; font-weight: 700;
        }
        .st-key-page [role="radiogroup"] > label:nth-of-type(2):hover,
        .st-key-page [role="radiogroup"] > label:nth-of-type(2):has(input:checked) {
            background: #ffe0e0; border-left-color: #b42318;
        }
        </style>
        """, unsafe_allow_html=True)

    pages = ["🏠 ホーム", "📅 シフト", "👤 マイページ"]
    if can_manage_room():
        pages.append("🏫 合同研究室")
    if st.session_state.is_host:
        pages.append("👑 管理")
    if st.session_state.get("page") not in pages:
        st.session_state.page = pages[0]
    st.sidebar.title("J-EXCHANGE SPARK")
    st.sidebar.write(f"ログイン中：{st.session_state.user_name}")
    # 画面切り替えをサイドバーにまとめ、選択中の画面だけを実行する。
    shift_label = f"📅 シフト提出（未回答 {len(pending)}件）" if pending else "📅 シフト提出"
    page_labels = {"🏠 ホーム": "🏠 ホーム", "📅 シフト": shift_label,
                   "👤 マイページ": "👤 自分の登録情報",
                   "👑 管理": "👑 運営・管理", "🏫 合同研究室": "🏫 合同研究室の管理"}
    view_mode = st.sidebar.radio("メニュー", pages, key="page",
                                 format_func=lambda page: page_labels[page])
    st.sidebar.divider()
    if st.sidebar.button("ログアウト"):
        st.session_state.clear()
        st.rerun()

    if view_mode == "🏠 ホーム":
        st.title("活動カレンダー")
        if not st.session_state.is_super and profile_missing_fields(current_user):
            info_message("初回の方は「自分の登録情報」で、ふりがな〜学科を入力して保存してください。")
            st.button("自分の登録情報を入力する", on_click=go_to_profile)
        if pending:
            notification, action = st.columns([3, 2])
            notification.error(f"未回答のシフト：あと{len(pending)}件")
            action.button("シフトを提出する", on_click=go_to_shift, type="primary", width="stretch")
        st.caption("予定をタップして詳細を見る")
        if "calendar_month" not in st.session_state:
            st.session_state.calendar_month = today.replace(day=1)
        month = st.session_state.calendar_month
        with st.container(key="calendar-layout"):
            calendar_panel, today_panel = st.columns([3, 1], gap="medium")
            with calendar_panel:
                with st.container(key="month-nav"):
                    previous, current, following = st.columns(3)
                    previous.button("← 前月", key="calendar_previous", on_click=change_calendar_month,
                                    args=(-1,), disabled=month == date.min, width="stretch")
                    if current.button("今月", key="calendar_current", width="stretch"):
                        st.session_state.calendar_month = today.replace(day=1)
                        st.session_state.pop("selected_activity", None)
                        st.rerun()
                    following.button("次月 →", key="calendar_next", on_click=change_calendar_month,
                                     args=(1,), disabled=month == date(9999, 12, 1), width="stretch")
                month_responses = [r for r in activities if r["day"] and
                                   (r["day"].year, r["day"].month) == (month.year, month.month)
                                   and r.get("requires_response", True)]
                deadline_groups = {}
                for row in month_responses:
                    if row["deadline"]:
                        deadline_groups.setdefault(row["deadline"], []).append(row)
                for deadline_day, rows in sorted(deadline_groups.items()):
                    scope = f"{month.month}月分のシフト" if len(rows) == len(month_responses) else f"{month.month}月のシフト（一部の予定）"
                    message = f"{scope}回答期限：{deadline_day.strftime('%Y/%m/%d')} 23:59まで"
                    if deadline_day < today:
                        st.error(f"{message} — 回答期限を過ぎています")
                    else:
                        info_message(message)
                show_calendar(month, activities, today)
                if not activities:
                    info_message("活動日程はまだ登録されていません。")
                else:
                    month_activities = [r for r in activities if r["day"] and
                                        (r["day"].year, r["day"].month) == (month.year, month.month)]
                    if not month_activities:
                        info_message("この月の予定はまだ登録されていません。")
                    if undated:
                        with st.expander("活動年が未登録の予定"):
                            for row in undated:
                                if st.button(activity_title(row["label"]), key=f"undated-event-{row['label']}"):
                                    st.session_state.selected_activity = row["label"]
            with today_panel:
                with st.container(border=True):
                    st.subheader("今日の活動")
                    st.caption(f"{today.month}月{today.day}日")
                    today_activities = [row for row in activities if row["day"] == today]
                    if not today_activities:
                        st.write("今日は活動予定がありません。")
                    for row in today_activities:
                        event_button(row, "today")
        if st.session_state.get("selected_activity"):
            show_activity_details(st.session_state.selected_activity)

    elif view_mode == "🏫 合同研究室":
        st.title("池澤先生の合同研究室")
        if not can_manage_room():
            st.error("統括管理者と先生モードだけが利用できます。")
            st.stop()
        if st.session_state.is_super:
            demo = st.toggle("架空のメンバーで動作確認する", key="room_demo_enabled")
        else:
            demo = False
        if demo:
            show_room_manager({"label": "デモ：オンラインセッション", "kind": "セッション"}, demo=True)
        else:
            eligible = [row for row in activities if room_eligible(row)]
            if eligible:
                label = st.selectbox("活動を選択", [row["label"] for row in eligible], key="room_event")
                show_room_manager(next(row for row in eligible if row["label"] == label))
            else:
                info_message("研究室を予約できるオンライン活動がありません。")

    elif view_mode == "📅 シフト":
        st.title("📅 シフト提出")
        if st.session_state.is_super:
            info_message("統括アカウントは回答できません。「管理」で回答一覧を確認してください。")
        elif not any(r.get("requires_response", True) for r in activities):
            info_message("現在、回答できる日程はありません。")
        else:
            if pending:
                st.error(f"未回答：あと{len(pending)}件")
            else:
                st.success("今後の活動へのシフト提出は完了しています。")
            if st.toggle("提出済みのシフトを確認", key="shift_review"):
                show_saved_shifts(activities, answers)
            else:
                st.caption("予定を開いて回答し、保存してください。")
                include_past = st.toggle("過去の予定も表示", key="shift_include_past")
                visible_activities = [r for r in (activities if include_past else upcoming + undated)
                                      if r.get("requires_response", True)]
                if not visible_activities:
                    info_message("今後の回答対象はありません。")
                with st.form("shift_answers"):
                    submitted_top = st.form_submit_button("回答を保存する", type="primary", width="stretch",
                                                          key="shift_save_top", disabled=not visible_activities)
                    edits = {}
                    room_edits = {}
                    for row_index, row in enumerate(visible_activities):
                        label = row["label"]
                        day_label = f"{row['day'].month}/{row['day'].day}" if row["day"] else "日付確認中"
                        status = "🔴 未" if activity_pending(row, answers) else "✓ 済"
                        identifier = hashlib.sha256(label.encode()).hexdigest()[:16]
                        with st.container(key=f"shift-event-{event_tone(row)}-{identifier}"):
                            with st.expander(f"{status}　{day_label}　{activity_title(label)}", expanded=row_index == 0):
                                if row["deadline"]:
                                    st.caption(f"回答期限：{row['deadline'].month}/{row['deadline'].day} 23:59まで")
                                    if row["deadline"] < today:
                                        st.error("回答期限を過ぎています")
                                if row.get("kind") == "セッション":
                                    if not any(part_column(label, part) in answers for part, _ in SESSION_PARTS) and answer_for(answers, label) != "未回答":
                                        st.caption("以前の回答を、前半・後半ごとに再確認してください。")
                                    with st.container(key=f"shift-parts-{hashlib.sha256(label.encode()).hexdigest()[:16]}"):
                                        for panel, (part, hours) in zip(st.columns(2), SESSION_PARTS):
                                            with panel:
                                                column = part_column(label, part)
                                                edits[column] = st.selectbox(part, ANSWER_OPTIONS,
                                                    index=ANSWER_OPTIONS.index(answer_for(answers, column)), key=f"answer_{column}")
                                                st.caption(hours)
                                    edits[label] = aggregate_parts([edits[part_column(label, part)] for part, _ in SESSION_PARTS])
                                else:
                                    st.caption(activity_time(label))
                                    edits[label] = st.selectbox("出欠", ANSWER_OPTIONS,
                                        index=ANSWER_OPTIONS.index(answer_for(answers, label)), key=f"answer_{label}")
                                comment_column = f"{label}｜コメント"
                                saved_comment = answers.get(comment_column, "")
                                edits[comment_column] = st.text_input("一言コメント（任意）",
                                    value="" if pd.isna(saved_comment) else str(saved_comment),
                                    key=f"comment_{label}", max_chars=200)
                                if room_eligible(row):
                                    config = room_config(label)
                                    room_edits[label] = st.checkbox("池澤先生の合同研究室の利用を希望する",
                                        value=room_wanted(label, st.session_state.user_email), key=f"room_wish_{label}")
                                    if config["status"] == "許可待ち":
                                        st.caption("先生の許可待ち・予約は未確定です。参加する時間帯だけが利用対象になります。")
                                    elif config["status"] == "利用不可":
                                        st.caption("この日は利用できません。希望は残せますが、予約は確定しません。")
                                    else:
                                        st.caption("利用可。定員内なら自動確定し、定員超過時は統括・先生が利用者を選びます。")
                                    own_results = room_results(room_candidates(row, load_csv(CSV_MEMBERS), load_csv(CSV_SCHEDULE), room_wishes(label)), config)
                                    for slot, result in own_results.items():
                                        own = normalize_email(st.session_state.user_email)
                                        if own in result["people"]:
                                            state = "利用確定" if own in result["confirmed"] else ("今回は選定されていません" if result["state"] == "利用者の選定済み" else result["state"])
                                            st.caption(f"保存済みの希望 · {slot}：{state}")
                    submitted_bottom = st.form_submit_button("回答を保存する", type="primary", width="stretch",
                                                             key="shift_save_bottom", disabled=not visible_activities)
                    submitted = submitted_top or submitted_bottom
                if submitted:
                    # 再読込して自分の回答列のみを更新し、既存の回答列も保持する。
                    df = load_csv(CSV_SCHEDULE)
                    if df.empty:
                        df = pd.DataFrame(columns=["更新日時", "名前"])
                    mask = df["名前"] == st.session_state.user_name
                    record = df[mask].iloc[-1].to_dict() if mask.any() else {}
                    record.update(edits)
                    record.update({"名前": st.session_state.user_name, "更新日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    df = pd.concat([df[~mask], pd.DataFrame([record])], ignore_index=True)
                    save_csv(df, CSV_SCHEDULE)
                    save_room_wishes(room_edits)
                    st.session_state.shift_saved = True
                    st.rerun()
                if st.session_state.pop("shift_saved", False):
                    st.success("回答を保存しました。")

    # --- 👤 ユーザー画面（マイページ） ---
    elif view_mode == "👤 マイページ":
        st.title("👤 自分の登録情報")
        
        if st.session_state.is_super:
            info_message("統括アカウントには個人プロフィールがありません。「管理」で操作してください。")
        else:
            df_members = load_csv(CSV_MEMBERS)
            norm_email = normalize_email(st.session_state.user_email)
            df_members['検索用メール'] = df_members['メールアドレス'].apply(normalize_email)
            user_data = df_members[df_members['検索用メール'] == norm_email].iloc[-1]
            if profile_missing_fields(user_data):
                info_message("ふりがな・役職・学年・学部・学科を確認し、「プロフィールを保存する」を押してください。")
            
            def_kana = user_data.get('ふりがな', '') if pd.notna(user_data.get('ふりがな', '')) else ""
            def_role = user_data.get('役職', ROLES[0]) if user_data.get('役職', '') in ROLES else ROLES[0]
            def_grade = user_data.get('学年', GRADES[0]) if user_data.get('学年', '') in GRADES else GRADES[0]
            def_loc = user_data.get('居住地(最寄り等)', '') if pd.notna(user_data.get('居住地(最寄り等)', '')) else ""
            def_note = user_data.get('補足情報', '') if pd.notna(user_data.get('補足情報', '')) else ""
            
            saved_fac = user_data.get('学部', '')
            saved_dept = user_data.get('学科', '')
            saved_course = user_data.get('専攻', '')
            
            def_fac = saved_fac if saved_fac in KANSAI_UNI_HIERARCHY else "選択してください"
            dept_dict_init = KANSAI_UNI_HIERARCHY[def_fac]
            def_dept = saved_dept if saved_dept in dept_dict_init else list(dept_dict_init.keys())[0]
            
            st.subheader("📝 基本情報")
            st.text_input("名前（変更不可）", value=st.session_state.user_name, disabled=True)
            st.text_input("メールアドレス（変更不可）", value=st.session_state.user_email, disabled=True)
            kana = st.text_input("ふりがな", value=def_kana)
            role = st.selectbox("役職", ROLES, index=ROLES.index(def_role))
            grade = st.selectbox("学年", GRADES, index=GRADES.index(def_grade))
            
            faculty = st.selectbox("学部", list(KANSAI_UNI_HIERARCHY.keys()), index=list(KANSAI_UNI_HIERARCHY.keys()).index(def_fac))
            dept_dict = KANSAI_UNI_HIERARCHY[faculty]
            dept_list = list(dept_dict.keys())
            dept_idx = dept_list.index(def_dept) if def_dept in dept_list else 0
            
            if len(dept_list) == 1 and dept_list[0] not in ["選択してください", "その他"]:
                st.text_input("学科", value=dept_list[0], disabled=True)
                department = dept_list[0]
            else:
                department = st.selectbox("学科", dept_list, index=dept_idx)
            
            course_list = dept_dict.get(department, [])
            course = ""
            if course_list:
                course_idx = course_list.index(saved_course) if saved_course in course_list else 0
                course = st.selectbox("専攻・コース・専修", course_list, index=course_idx)
            
            with st.expander("詳細情報（居住地・補足）"):
                location = st.text_input("居住地・最寄り駅など", value=def_loc)
                note = st.text_area("補足情報（留学予定、長期休みの状況など）", value=def_note)
            

            if st.button("プロフィールを保存する", type="primary"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_members = load_csv(CSV_MEMBERS)
                own_rows = df_members[df_members['メールアドレス'].apply(normalize_email) == norm_email].index
                if own_rows.empty or credential_fingerprint(df_members.loc[own_rows[-1], 'パスワードハッシュ']) != st.session_state.auth_fingerprint:
                    st.session_state.clear()
                    st.rerun()
                updates = {'更新日時': now, 'ふりがな': kana, '役職': role, '学部': faculty,
                           '学科': department, '専攻': course, '学年': grade, '居住地(最寄り等)': location, '補足情報': note}
                for column, value in updates.items():
                    df_members.loc[own_rows, column] = value
                save_csv(df_members, CSV_MEMBERS)
                
                st.success("✅ 情報を更新しました！")

    # --- 👑 ホスト画面 ---
    elif view_mode == "👑 管理":
        if not st.session_state.is_host:
            st.error("管理者だけが利用できます。")
            st.stop()
        st.title("👑 管理")
        
        admin_options = ['日程設定', 'シフト回答状況', 'メンバー名簿', '権限一覧', 'メンバー登録', '削除']
        if st.session_state.is_super:
            admin_options.extend(['参加意思の確認', '管理者設定'])
        admin_action = st.selectbox('管理メニュー', admin_options, key='admin_section')

        # ホストも一般メンバーを登録できる。権限付与は統括だけに限定する。
        if st.session_state.is_host:
            if admin_action == 'メンバー登録':
                st.subheader("➕ 新規メンバーの登録")
                st.write("J-EXCHANGE SPARKに参加するメンバーを事前登録します。ここで設定した初期パスワードを本人に伝えてください。")
                
                with st.form("register_member_form"):
                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        new_name = st.text_input("名前（フルネーム）")
                        new_email = st.text_input("メールアドレス（@より前）", help="@kansai-u.ac.jp は自動で補います。")
                        new_pass = st.text_input("初期パスワード", type="password")
                    with col_r2:
                        new_role = st.selectbox("役職", ROLES)
                        new_is_host = st.checkbox("このメンバーにホスト権限を付与する") if st.session_state.is_super else False
                    
                    if st.form_submit_button("メンバーを登録する"):
                        df_members = load_csv(CSV_MEMBERS)
                        norm_new_email = university_email(new_email)
                        
                        if not new_name or not new_email or not new_pass:
                            st.error("名前、メールアドレス、初期パスワードは必須です。")
                        elif norm_new_email is None:
                            st.error("関西大学のメールアドレスを入力してください。")
                        elif not df_members.empty and norm_new_email in df_members['メールアドレス'].apply(normalize_email).values:
                            st.error("このメールアドレスは既に登録されています。")
                        elif not df_members.empty and new_name.strip() in df_members['名前'].astype(str).str.strip().values:
                            st.error("同じ名前のメンバーが登録されています。識別できるよう名前に学年などを添えてください。")
                        else:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            hashed_pass = hash_password(new_pass)
                            new_member = pd.DataFrame([[
                                now, new_name, norm_new_email, hashed_pass, False, bool(st.session_state.is_super and new_is_host),
                                "", new_role, "選択してください", "選択してください", "", GRADES[0], "", ""
                            ]], columns=[
                                '更新日時', '名前', 'メールアドレス', 'パスワードハッシュ', '初回パスワード変更済み', 'ホスト権限', 
                                'ふりがな', '役職', '学部', '学科', '専攻', '学年', '居住地(最寄り等)', '補足情報'
                            ])
                            new_member['登録日'] = today_japan().isoformat()
                            df_members = pd.concat([df_members, new_member], ignore_index=True)
                            save_csv(df_members, CSV_MEMBERS)
                            st.success(f"✅ {new_name} さん（{new_email}）を登録しました！本人に初期パスワードを伝えてください。")

        if admin_action == '権限一覧':
            st.subheader('権限を持つメンバー')
            people = []
            for member in load_csv(CSV_MEMBERS).to_dict('records'):
                host = parse_bool(member.get('ホスト権限', False))
                teacher = parse_bool(member.get('先生モード', False))
                if host or teacher:
                    people.append({'名前': member['名前'], '利用者ID': normalize_email(member['メールアドレス']).split('@')[0],
                                   'ホスト': 'あり' if host else '—', '池澤先生モード': 'あり' if teacher else '—'})
            if people:
                st.dataframe(pd.DataFrame(people), hide_index=True, width='stretch')
            else:
                info_message('権限を持つ登録メンバーはいません。')
            st.caption('統括管理者の専用ログインは、この一覧とは別です。権限の変更は「管理者設定」で行います。')

        if admin_action == '参加意思の確認':
            show_participation_review(activities)

        if admin_action == 'シフト回答状況':
            st.subheader("みんなのシフト回答状況")
            df_schedule = load_csv(CSV_SCHEDULE)
            response_activities = [row for row in activities if row.get('requires_response', True)]
            if response_activities:
                label = st.selectbox('確認する予定', [row['label'] for row in response_activities], key='admin_shift_event')
                row = next(row for row in response_activities if row['label'] == label)
                st.caption(activity_time(label))
                records = {} if df_schedule.empty else df_schedule.drop_duplicates('名前', keep='last').set_index('名前').to_dict('index')
                display = []
                completed = 0
                for member in load_csv(CSV_MEMBERS).to_dict('records'):
                    answers_row = records.get(member['名前'], {})
                    completed += not activity_pending(row, answers_row)
                    entry = {'名前': member['名前']}
                    if row['kind'] == 'セッション':
                        for part, _ in SESSION_PARTS:
                            entry[part] = answer_for(answers_row, part_column(label, part))
                    else:
                        entry['出欠'] = answer_for(answers_row, label)
                    comment = answers_row.get(f'{label}｜コメント', '')
                    entry['コメント'] = '' if pd.isna(comment) else str(comment)
                    display.append(entry)
                summary = st.columns(3)
                summary[0].metric('回答済み', f'{completed}名')
                summary[1].metric('未回答あり', f'{len(display) - completed}名')
                summary[2].metric('参加希望', f"{sum(any(value == ANSWER_OPTIONS[1] for key, value in entry.items() if key in ['前半', '後半', '出欠']) for entry in display)}名")
                answer_filter = st.selectbox('表示する回答', ['全員', '参加希望あり', '未回答あり', '未定あり', '欠席のみ'], key='shift_answer_filter')
                search = st.text_input('名前で検索', key='shift_member_search')
                visible = []
                short = {ANSWER_OPTIONS[0]: '🔴 未', ANSWER_OPTIONS[1]: '参加', ANSWER_OPTIONS[2]: '欠席', ANSWER_OPTIONS[3]: '未定'}
                for entry in display:
                    values = [value for key, value in entry.items() if key in ['前半', '後半', '出欠']]
                    matches = answer_filter == '全員' or (answer_filter == '参加希望あり' and ANSWER_OPTIONS[1] in values) or (answer_filter == '未回答あり' and ANSWER_OPTIONS[0] in values) or (answer_filter == '未定あり' and ANSWER_OPTIONS[3] in values) or (answer_filter == '欠席のみ' and all(v == ANSWER_OPTIONS[2] for v in values))
                    if matches and search.strip() in entry['名前']:
                        visible.append({key: short.get(value, value) if key in ['前半', '後半', '出欠'] else value for key, value in entry.items()})
                st.dataframe(pd.DataFrame(visible, columns=list(display[0]) if display else ['名前']), width='stretch', hide_index=True)
                st.caption('前半 13:30～14:30 ／ 後半 14:30～15:30' if row['kind'] == 'セッション' else '参加希望・未回答を絞り込んで確認できます。')
            else:
                info_message("回答対象の予定がありません。")
                
        if admin_action == 'メンバー名簿':
            st.subheader("J-EXCHANGE SPARK メンバー名簿")
            df_members = load_csv(CSV_MEMBERS)
            if not df_members.empty:
                filter_role = st.selectbox("役職で絞り込み", ["すべて表示"] + ROLES)
                # セキュリティに関わる列を隠す
                display_members = df_members.drop(columns=['パスワードハッシュ', '初回パスワード変更済み', 'ホスト権限', '先生モード', '更新日時', 'パスワード'], errors='ignore')
                if filter_role != "すべて表示":
                    display_members = display_members[display_members['役職'] == filter_role]
                st.dataframe(display_members, use_container_width=True, hide_index=True)
            else:
                info_message("まだ登録メンバーがいません。")
                
        if admin_action == '日程設定':
            with st.expander('登録済みの予定を変更する'):
                show_activity_editor()
            with st.expander("月ごとの回答期限を設定"):
                st.caption("この月の回答対象すべてに適用します。後から追加する予定にも適用され、個別の期限より優先されます。")
                target_month = st.date_input("対象月（月内の日付を選択）", value=today.replace(day=1), key="deadline_month")
                monthly_deadline = st.date_input("月全体の回答期限", key="monthly_deadline")
                if st.button("月の回答期限を保存", key="save_monthly_deadline"):
                    month_rows = [r for r in activity_rows() if r["day"] and
                                  (r["day"].year, r["day"].month) == (target_month.year, target_month.month)
                                  and r.get("requires_response", True)]
                    if month_rows and monthly_deadline > min(r["day"] for r in month_rows):
                        st.error("回答期限は、この月の最初の活動日以前にしてください。")
                    else:
                        monthly = load_csv(CSV_MONTH_DEADLINES)
                        month_key = target_month.strftime("%Y-%m")
                        if not monthly.empty:
                            monthly = monthly[monthly["対象月"] != month_key]
                        monthly = pd.concat([monthly, pd.DataFrame([{"対象月": month_key, "回答期限": monthly_deadline.isoformat()}])], ignore_index=True)
                        save_csv(monthly, CSV_MONTH_DEADLINES)
                        st.success(f"{target_month.year}年{target_month.month}月分の回答期限を保存しました。")
            st.subheader("新しい日程の追加")
            if st.session_state.notification_text:
                info_message("💡 以下のテキストをコピーして、Discordのお知らせチャンネルに共有してください。")
                st.code(st.session_state.notification_text, language="text")
                if st.button("メッセージを閉じる"):
                    st.session_state.notification_text = ""
                    st.rerun()
                st.divider()

            st.write("📅 イベントの種類と日程を設定してください")
            event_type = st.selectbox("イベントの種類", ["セッション", "オンライン会議", "オフライン会議", "その他（自由記述）"])
            
            event_title = event_type
            if event_type in ["オンライン会議", "オフライン会議"]:
                meeting_name = st.text_input("会議名（任意）", placeholder="例：企画ミーティング")
                event_title = meeting_name.strip() or event_type
            elif event_type == "その他（自由記述）":
                event_title = st.text_input("イベントのタイトルを入力してください")
            
            col_d, col_t1, col_t2 = st.columns([2, 1, 1])
            with col_d:
                selected_date = st.date_input("日付")
            with col_t1:
                start_time = st.time_input("開始時間", value=time(13, 30) if event_type == "セッション" else time(13, 0), disabled=event_type == "セッション")
            with col_t2:
                end_time = st.time_input("終了時間", value=time(15, 30) if event_type == "セッション" else time(17, 0), disabled=event_type == "セッション")
            
            requires_response = st.checkbox("参加可否を募る", value=True,
                                             help="オフにすると、お知らせとしてカレンダーに表示します。シフト回答は不要です。")
            if st.session_state.pop('reset_new_event_room', False):
                st.session_state.new_event_room_enabled = False
            room_enabled = st.checkbox("池澤先生の合同研究室利用希望を追加する", value=False,
                                       disabled=not requires_response, key="new_event_room_enabled",
                                       help="チェックした予定だけに利用申請欄を表示します。参加可否の回答と連動します。")
            use_deadline = st.checkbox("回答期限を設定する") if requires_response else False
            deadline = st.date_input("回答期限（日付の終わりまで）") if use_deadline else None

            if st.button("日程を追加"):
                if event_type == "その他（自由記述）" and not event_title.strip():
                    st.error("イベントのタイトルを入力してください。")
                elif end_time <= start_time:
                    st.error("終了時間は開始時間より後にしてください。")
                elif deadline and deadline > selected_date:
                    st.error("回答期限は活動日以前にしてください。")
                else:
                    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
                    w = weekdays[selected_date.weekday()]
                    new_date_str = f"【{event_title}】 {selected_date.year}年{selected_date.month}月{selected_date.day}日({w}) {start_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}"
                    
                    target_dates_df = load_csv(CSV_DATES)
                    if new_date_str not in target_dates_df['日程'].values:
                        new_row = pd.DataFrame({'日程': [new_date_str], '活動日': [selected_date.isoformat()], '回答期限': [deadline.isoformat() if deadline else ''], 'イベント種類': [event_type], '参加可否を募る': [requires_response], '合同研究室利用希望': [bool(requires_response and room_enabled)]})
                        target_dates_df = pd.concat([target_dates_df, new_row], ignore_index=True)
                        save_csv(target_dates_df, CSV_DATES)
                        
                        df_schedule = load_csv(CSV_SCHEDULE)
                        if requires_response and not df_schedule.empty:
                            df_schedule[new_date_str] = "未回答"
                            save_csv(df_schedule, CSV_SCHEDULE)
                        
                        app_url = "※ここに公開後のアプリのURLが入ります"
                        request_text = "シフト・出欠の回答をお願いします！" if requires_response else "お知らせをご確認ください（参加可否の回答は不要です）。"
                        st.session_state.notification_text = f"お疲れ様です！J-EXCHANGE SPARKの新しい日程が追加されました。\n\n対象: {new_date_str}\n\n以下のURLからログインし、{request_text}\n{app_url}"
                        
                        st.success(f"「{new_date_str}」を追加しました！")
                        st.session_state.reset_new_event_room = True
                        st.rerun()
                    else:
                        st.warning("その日程はすでに追加されています。")

        if admin_action == '削除':
            st.subheader('日程・メンバーの削除')
            st.caption('複数選択できます。選んだ対象を確認してから削除してください。')
            dates = load_csv(CSV_DATES)
            if not dates.empty:
                selected_events = st.multiselect('削除する日程', dates['日程'].tolist(), key='delete_events',
                                                on_change=reset_delete_confirmation, args=('confirm_delete_events',))
                if selected_events:
                    st.write(f'日程 {len(selected_events)}件を削除します。回答・コメント・研究室予約も削除されます。')
                    st.text('\n'.join(selected_events))
                confirmed = st.checkbox('選択した日程を削除することを確認しました', key='confirm_delete_events')
                if st.button('この日程を完全に削除する', disabled=not selected_events or not confirmed):
                    try:
                        count = delete_activities(selected_events)
                        st.session_state.delete_notice = f'日程 {count}件を削除しました。'
                        st.rerun()
                    except (PermissionError, ValueError) as error:
                        st.error(str(error))
            else:
                info_message('削除できる日程がありません。')
            if st.session_state.is_super:
                st.divider()
                members = load_csv(CSV_MEMBERS)
                if not members.empty:
                    names = dict(zip(members['メールアドレス'], members['名前']))
                    selected_members = st.multiselect('削除するメンバー', list(names), format_func=lambda email: f'{names[email]} ({email})', key='delete_members',
                                                     on_change=reset_delete_confirmation, args=('confirm_delete_members',))
                    if selected_members:
                        st.write(f'メンバー {len(selected_members)}名を削除します。シフト回答・研究室の利用希望も削除されます。')
                        st.text('\n'.join(f'{names[email]} ({email})' for email in selected_members))
                    confirmed_members = st.checkbox('選択したメンバーを削除することを確認しました', key='confirm_delete_members')
                    if st.button('このメンバーを完全に削除する', disabled=not selected_members or not confirmed_members):
                        try:
                            count = delete_members(selected_members)
                            st.session_state.delete_notice = f'メンバー {count}名を削除しました。'
                            st.rerun()
                        except (PermissionError, ValueError) as error:
                            st.error(str(error))
                else:
                    info_message('削除できるメンバーがいません。')
            if st.session_state.get('delete_notice'):
                st.success(st.session_state.pop('delete_notice'))

        if st.session_state.is_super:
            if admin_action == '管理者設定':
                st.subheader("🛠️ 管理者設定（権限・パスワードリセット）")
                df_members = load_csv(CSV_MEMBERS)
                if not df_members.empty:
                    member_list = [f"{row['名前']} ({row['メールアドレス']})" for idx, row in df_members.iterrows()]
                    selected_member_str = st.selectbox("設定を変更するユーザーを選択してください", member_list)
                    
                    if selected_member_str:
                        target_email = selected_member_str.split('(')[-1].strip(')')
                        norm_target_email = normalize_email(target_email)
                        target_idx = df_members[df_members['メールアドレス'].apply(normalize_email) == norm_target_email].index
                        target_name = df_members.loc[target_idx, '名前'].values[0]
                        current_status = parse_bool(df_members.loc[target_idx, 'ホスト権限'].values[0])
                        
                        st.write(f"**{target_name} さんの設定変更**")
                        
                        # 権限変更
                        new_status = st.checkbox(f"👑 ホスト権限を付与する", value=current_status)
                        teacher_status = st.checkbox("🏫 池澤先生モードを付与する", value=parse_bool(df_members.loc[target_idx, '先生モード'].values[0]),
                                                     help="ホスト権限とは独立しています。合同研究室の利用許可と利用者の選定ができます。")
                        
                        # メアド変更
                        new_email_edit = st.text_input("メールアドレスの変更（@より前）", value=target_email.split("@")[0],
                                                       help="@kansai-u.ac.jp は自動で補います。")
                        
                        # パスワードリセット
                        reset_pass = st.text_input("初期パスワードの再設定（変更する場合のみ入力）", type="password")
                        
                        if st.button("設定を更新する"):
                            new_email_edit = university_email(new_email_edit)
                            # メアド変更時の重複チェック
                            if not new_email_edit:
                                st.error("関西大学のメールアドレスを入力してください。")
                            elif normalize_email(new_email_edit) != norm_target_email and normalize_email(new_email_edit) in df_members['メールアドレス'].apply(normalize_email).values:
                                st.error("そのメールアドレスは他のユーザーが既に使用しています。")
                            else:
                                df_members.loc[target_idx, 'ホスト権限'] = new_status
                                df_members.loc[target_idx, '先生モード'] = teacher_status
                                if normalize_email(new_email_edit) != norm_target_email:
                                    with room_connection() as connection:
                                        connection.execute("UPDATE wishes SET email=? WHERE email=?", (normalize_email(new_email_edit), norm_target_email))
                                        connection.execute("UPDATE participation_reviews SET email=? WHERE email=?", (normalize_email(new_email_edit), norm_target_email))
                                        for event, raw in connection.execute("SELECT event,config FROM settings").fetchall():
                                            config = json.loads(raw)
                                            for choice in config.get("choices", {}).values():
                                                for field in ["selected", "candidates"]:
                                                    choice[field] = [normalize_email(new_email_edit) if email == norm_target_email else email for email in choice.get(field, [])]
                                                choice["candidates"] = sorted(choice["candidates"])
                                            connection.execute("UPDATE settings SET config=? WHERE event=?", (json.dumps(config, ensure_ascii=False), event))
                                df_members.loc[target_idx, 'メールアドレス'] = new_email_edit
                                
                                if reset_pass:
                                    df_members.loc[target_idx, 'パスワードハッシュ'] = hash_password(reset_pass)
                                    df_members.loc[target_idx, '初回パスワード変更済み'] = False
                                
                                save_csv(df_members, CSV_MEMBERS)
                                st.success(f"✅ {target_name} さんの設定を更新しました！")
                else:
                    info_message("登録されているユーザーがいません。")
