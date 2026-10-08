import streamlit as st
import pandas as pd
import os
import hashlib
import re
import calendar
import csv
from pathlib import Path
from datetime import datetime, time, date, timedelta, timezone

# ==========================================
# 1. データの準備と設定
# ==========================================
st.set_page_config(page_title="J-EXCHANGE SPARK 管理アプリ", layout="wide")

# 白を基調に、操作する場所を緑で示す共通デザイン。
st.markdown("""
<style>
.stApp { background: #ffffff; color: #24352c; }
.stApp a { color: #14532d; }
[data-testid="stHeader"] { background: #ffffff; }
[data-testid="stMainBlockContainer"] { max-width: 100%; padding: 2rem clamp(1rem, 3vw, 3rem) 4rem; }
[data-testid="stSidebar"] { background: #f4f8f5; border-right: 1px solid #dce9e1; }
[data-testid="stMarkdownContainer"] p { line-height: 1.75; }
[data-testid="stCaptionContainer"] { color: #526158; }
[data-testid="stWidgetLabel"] p { font-weight: 600; }
h1, h2, h3 { color: #30574b; letter-spacing: .015em; }
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
.spark-brand { color: #3c7764; font-weight: 800; font-size: .85rem; letter-spacing: .16em; }
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
[data-testid="stStatusWidget"], [data-testid="stMainMenu"],
[data-testid="stGithubIcon"], [data-testid="stGitHubIcon"],
[data-testid="stHostedAppBadge"], [class*="_viewerBadge"],
.stApp a[href^="https://github.com/"][target="_blank"]:has(svg) { display: none !important; }
.st-key-shift_answers [data-testid="stExpander"] { border-radius: 6px; }
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
    """パスワードをSHA-256でハッシュ化する"""
    return hashlib.sha256(str(password).encode('utf-8')).hexdigest()

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
            required_cols = ['メールアドレス', 'パスワードハッシュ', '初回パスワード変更済み', '専攻']
            for col in required_cols:
                if col not in df.columns:
                    if col == '初回パスワード変更済み':
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
                     "deadline": read_date(record.get("回答期限")), "order": legacy_order})
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
    if not st.session_state.get("logged_in"):
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
    df.to_csv(CSV_DATES, index=False)
    return True


def close_activity_details():
    st.session_state.pop("selected_activity", None)


@st.dialog("予定の詳細", width="large", on_dismiss=close_activity_details)
def show_activity_details(label):
    row = next((r for r in activity_rows() if r["label"] == label), None)
    if row is None:
        info_message("この予定は削除されています。")
        return
    st.subheader(activity_title(label))
    st.caption(activity_time(label))
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
        st.subheader(f"参加予定者（{len(names)}人）")
        if names:
            st.text("、".join(names))
        else:
            st.write("まだいません")
    st.subheader("当日の共有メモ")
    if can_edit_activity_memo():
        with st.form("activity_memo_form"):
            memo = st.text_area("集合場所・持ち物・注意事項など", value=row["memo"],
                                key=f"memo_{label}", height=160)
            submitted = st.form_submit_button("共有メモを保存する", type="primary")
        if submitted:
            if save_activity_memo(label, memo):
                st.success("保存しました。全員がこの予定の詳細から確認できます。")
            else:
                st.error("予定が削除されたため保存できませんでした。")
    elif row["memo"]:
        st.text(row["memo"])
    else:
        st.write("なし")


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
if not st.session_state.logged_in:
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
            if input_email and input_pass:
                norm_email = university_email(input_email, allow_admin=True)
                if norm_email is None:
                    st.error("関西大学のメールアドレスを入力してください。")
                    st.stop()
                
                # ① 統括管理者のログイン判定
                if norm_email == normalize_email(SUPER_ADMIN_NAME) and SUPER_ADMIN_PASS and input_pass == SUPER_ADMIN_PASS:
                    st.session_state.logged_in = True
                    st.session_state.user_name = "統括管理者"
                    st.session_state.user_email = SUPER_ADMIN_NAME
                    st.session_state.is_host = True
                    st.session_state.is_super = True
                    st.session_state.must_change_password = False
                    st.rerun()
                else:
                    df_members = load_csv(CSV_MEMBERS)
                    if df_members.empty:
                        st.error("メンバーが一人も登録されていません。運営に登録を依頼してください。")
                    else:
                        # メールアドレスでユーザーを検索
                        df_members['検索用メール'] = df_members['メールアドレス'].apply(normalize_email)
                        matched_users = df_members[df_members['検索用メール'] == norm_email]
                        
                        if matched_users.empty:
                            st.error("このメールアドレスはJ-EXCHANGE SPARKに登録されていません。運営に登録を依頼してください。")
                        else:
                            user_data = matched_users.iloc[-1]
                            # パスワードのハッシュ照合
                            if user_data['パスワードハッシュ'] == hash_password(input_pass):
                                st.session_state.logged_in = True
                                st.session_state.user_name = user_data['名前']
                                st.session_state.user_email = user_data['メールアドレス']
                                st.session_state.is_host = parse_bool(user_data.get('ホスト権限', False))
                                st.session_state.is_super = False
                                
                                # 初回ログイン判定
                                if not parse_bool(user_data.get('初回パスワード変更済み', False)):
                                    st.session_state.must_change_password = True
                                else:
                                    st.session_state.must_change_password = False
                                
                                st.rerun()
                            else:
                                st.error("⚠️ パスワードが違います。")
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
            else:
                # パスワードを更新
                df_members = load_csv(CSV_MEMBERS)
                norm_email = normalize_email(st.session_state.user_email)
                df_members['検索用メール'] = df_members['メールアドレス'].apply(normalize_email)
                
                # 対象ユーザーの行を更新
                target_idx = df_members[df_members['検索用メール'] == norm_email].index
                df_members.loc[target_idx, 'パスワードハッシュ'] = hash_password(new_pass)
                df_members.loc[target_idx, '初回パスワード変更済み'] = True
                df_members.loc[target_idx, '更新日時'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 検索用列を消して保存
                df_members = df_members.drop(columns=['検索用メール'])
                df_members.to_csv(CSV_MEMBERS, index=False)
                
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
                   "👑 管理": "👑 運営・管理"}
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
                    for row_index, row in enumerate(visible_activities):
                        label = row["label"]
                        day_label = f"{row['day'].month}/{row['day'].day}" if row["day"] else "日付確認中"
                        status = "🔴 未" if activity_pending(row, answers) else "✓ 済"
                        identifier = hashlib.sha256(label.encode()).hexdigest()[:16]
                        with st.container(key=f"shift-event-{event_tone(row)}-{identifier}"):
                            with st.expander(f"{status}　{day_label}　{activity_title(label)}", expanded=row_index == 0):
                                if row["deadline"]:
                                    st.caption(f"回答期限：{row['deadline'].month}/{row['deadline'].day}")
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
                    df.to_csv(CSV_SCHEDULE, index=False)
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
                user_pass_hash = user_data['パスワードハッシュ']
                user_host = user_data['ホスト権限']
                has_changed_pass = user_data['初回パスワード変更済み']
                
                new_member_data = pd.DataFrame([[
                    now, st.session_state.user_name, st.session_state.user_email, user_pass_hash, has_changed_pass, user_host, 
                    kana, role, faculty, department, course, grade, location, note
                ]], columns=[
                    '更新日時', '名前', 'メールアドレス', 'パスワードハッシュ', '初回パスワード変更済み', 'ホスト権限', 
                    'ふりがな', '役職', '学部', '学科', '専攻', '学年', '居住地(最寄り等)', '補足情報'
                ])
                
                df_members = df_members.drop(columns=['検索用メール'])
                df_members = df_members[df_members['メールアドレス'].apply(normalize_email) != norm_email]
                df_members = pd.concat([df_members, new_member_data], ignore_index=True)
                df_members.to_csv(CSV_MEMBERS, index=False)
                
                st.success("✅ 情報を更新しました！")

    # --- 👑 ホスト画面 ---
    elif view_mode == "👑 管理":
        if not st.session_state.is_host:
            st.error("管理者だけが利用できます。")
            st.stop()
        st.title("👑 管理")
        
        if st.session_state.is_super:
            htab_reg, htab1, htab2, htab3, htab_del, htab4 = st.tabs(["➕ メンバー登録", "📋 シフト状況", "👥 メンバー名簿", "⚙️ 日程設定", "🗑️ データ削除", "🛠️ 管理者設定(統括)"])
        else:
            htab_reg, htab1, htab2, htab3, htab_del = st.tabs(["➕ メンバー登録", "📋 シフト回答状況", "👥 メンバー名簿", "⚙️ 日程の設定", "🗑️ 日程の削除"])
            
        # ホストも一般メンバーを登録できる。権限付与は統括だけに限定する。
        if st.session_state.is_host:
            with htab_reg:
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
                            df_members = pd.concat([df_members, new_member], ignore_index=True)
                            df_members.to_csv(CSV_MEMBERS, index=False)
                            st.success(f"✅ {new_name} さん（{new_email}）を登録しました！本人に初期パスワードを伝えてください。")

        with htab1:
            st.subheader("みんなのシフト回答状況")
            df_schedule = load_csv(CSV_SCHEDULE)
            if not df_schedule.empty:
                st.dataframe(df_schedule, use_container_width=True, hide_index=True)
            else:
                info_message("まだ回答がありません。")
                
        with htab2:
            st.subheader("J-EXCHANGE SPARK メンバー名簿")
            df_members = load_csv(CSV_MEMBERS)
            if not df_members.empty:
                filter_role = st.selectbox("役職で絞り込み", ["すべて表示"] + ROLES)
                # セキュリティに関わる列を隠す
                display_members = df_members.drop(columns=['パスワードハッシュ', '初回パスワード変更済み', 'ホスト権限', '更新日時', 'パスワード'], errors='ignore')
                if filter_role != "すべて表示":
                    display_members = display_members[display_members['役職'] == filter_role]
                st.dataframe(display_members, use_container_width=True, hide_index=True)
            else:
                info_message("まだ登録メンバーがいません。")
                
        with htab3:
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
                start_time = st.time_input("開始時間", value=time(13, 0))
            with col_t2:
                end_time = st.time_input("終了時間", value=time(17, 0))
            
            requires_response = st.checkbox("参加可否を募る", value=True,
                                             help="オフにすると、お知らせとしてカレンダーに表示します。シフト回答は不要です。")
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
                        new_row = pd.DataFrame({'日程': [new_date_str], '活動日': [selected_date.isoformat()], '回答期限': [deadline.isoformat() if deadline else ''], 'イベント種類': [event_type], '参加可否を募る': [requires_response]})
                        target_dates_df = pd.concat([target_dates_df, new_row], ignore_index=True)
                        target_dates_df.to_csv(CSV_DATES, index=False)
                        
                        df_schedule = load_csv(CSV_SCHEDULE)
                        if requires_response and not df_schedule.empty:
                            df_schedule[new_date_str] = "未回答"
                            df_schedule.to_csv(CSV_SCHEDULE, index=False)
                        
                        app_url = "※ここに公開後のアプリのURLが入ります"
                        request_text = "シフト・出欠の回答をお願いします！" if requires_response else "お知らせをご確認ください（参加可否の回答は不要です）。"
                        st.session_state.notification_text = f"お疲れ様です！J-EXCHANGE SPARKの新しい日程が追加されました。\n\n対象: {new_date_str}\n\n以下のURLからログインし、{request_text}\n{app_url}"
                        
                        st.success(f"「{new_date_str}」を追加しました！")
                        st.rerun()
                    else:
                        st.warning("その日程はすでに追加されています。")

        with htab_del:
            st.subheader("🗑️ データの削除")
            st.error("⚠️ 一度削除したデータは元に戻せません。慎重に操作してください。")
            
            if st.session_state.is_super:
                del_col1, del_col2 = st.columns(2)
            else:
                del_col1, del_col2 = st.container(), None
            
            with del_col1:
                st.write("**日程（スケジュール）の削除**")
                target_dates_df = load_csv(CSV_DATES)
                if not target_dates_df.empty:
                    date_to_delete = st.selectbox("削除する日程を選択", target_dates_df['日程'].tolist())
                    if st.button("この日程を完全に削除する"):
                        target_dates_df = target_dates_df[target_dates_df['日程'] != date_to_delete]
                        target_dates_df.to_csv(CSV_DATES, index=False)
                        
                        df_schedule = load_csv(CSV_SCHEDULE)
                        related_columns = [date_to_delete, f"{date_to_delete}｜コメント"] + [
                            part_column(date_to_delete, part) for part, _ in SESSION_PARTS]
                        present_columns = [column for column in related_columns if column in df_schedule.columns]
                        if present_columns:
                            df_schedule = df_schedule.drop(columns=present_columns)
                            df_schedule.to_csv(CSV_SCHEDULE, index=False)
                        
                        st.success(f"日程「{date_to_delete}」を削除しました。")
                        st.rerun()
                else:
                    info_message("削除できる日程がありません。")
            
            if st.session_state.is_super:
                with del_col2:
                    st.write("**メンバーの削除**")
                    df_members = load_csv(CSV_MEMBERS)
                    if not df_members.empty:
                        # 名前とメールアドレスのリストを作成
                        member_list = [f"{row['名前']} ({row['メールアドレス']})" for idx, row in df_members.iterrows()]
                    
                        if member_list:
                            selected_member_str = st.selectbox("削除するメンバーを選択", member_list)
                            confirm_delete = st.checkbox("本当にこのメンバーを削除しますか？（シフト回答も削除されます）")
                        
                            if st.button("このメンバーを完全に削除する"):
                                if not confirm_delete:
                                    st.error("削除する場合はチェックボックスにチェックを入れてください。")
                                else:
                                    target_email = selected_member_str.split('(')[-1].strip(')')
                                    norm_target_email = normalize_email(target_email)
                                    target_name = df_members[df_members['メールアドレス'].apply(normalize_email) == norm_target_email]['名前'].values[0]
                                
                                    df_members = df_members[df_members['メールアドレス'].apply(normalize_email) != norm_target_email]
                                    df_members.to_csv(CSV_MEMBERS, index=False)
                                
                                    df_schedule = load_csv(CSV_SCHEDULE)
                                    if not df_schedule.empty and target_name in df_schedule['名前'].values:
                                        df_schedule = df_schedule[df_schedule['名前'] != target_name]
                                        df_schedule.to_csv(CSV_SCHEDULE, index=False)
                                
                                    st.success(f"メンバー「{target_name}」を削除しました。")
                                    st.rerun()
                        else:
                            info_message("削除できるメンバーがいません。")

        if st.session_state.is_super:
            with htab4:
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
                                df_members.loc[target_idx, 'メールアドレス'] = new_email_edit
                                
                                if reset_pass:
                                    df_members.loc[target_idx, 'パスワードハッシュ'] = hash_password(reset_pass)
                                    df_members.loc[target_idx, '初回パスワード変更済み'] = False
                                
                                df_members.to_csv(CSV_MEMBERS, index=False)
                                st.success(f"✅ {target_name} さんの設定を更新しました！")
                else:
                    info_message("登録されているユーザーがいません。")
