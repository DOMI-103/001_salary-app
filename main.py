import datetime
import os.path
import pickle
from dateutil.relativedelta import relativedelta
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import streamlit as st

# スコープ設定
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# ===== 早稲アカ コマ定義 =====
WASEDA_KOMA = [
    ("Y", "10:40", "12:10"),
    ("Z", "12:20", "13:50"),
    ("A", "15:00", "16:30"),
    ("B", "16:40", "18:10"),
    ("C", "18:20", "19:50"),
    ("D", "20:00", "21:30"),
]

# ===== バイトごとの給料計算関数 =====
def calc_waseaka(hours, wage, work_days, koma_count):
    koma_wage = wage * 1.5
    salary = koma_count * koma_wage + 425 * work_days + koma_count * 215
    return salary

def calc_toraya(hours, wage, work_days):
    salary = (hours - 0.5 * work_days) * wage + 292 * work_days
    return salary

def calc_haluene(hours, wage, work_days):
    salary = hours * wage + 376 * work_days
    return salary

PARTTIME_JOBS = {
    "早稲アカ": {"wage": 1410, "calc_func": calc_waseaka},
    "とらや": {"wage": 1250, "calc_func": calc_toraya},
    "ハルエネ": {"wage": 1500, "calc_func": calc_haluene}
}

def get_service():
    if "credentials" in st.session_state:
        return build("calendar", "v3", credentials=st.session_state["credentials"])

    # Secretsから設定を読み込み
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": st.secrets["google"]["client_id"],
                "client_secret": st.secrets["google"]["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=st.secrets["google"]["redirect_uri"],
    )

    # 認証コードの確認
    code = st.query_params.get("code")
    if code:
        flow.fetch_token(code=code)
        st.session_state["credentials"] = flow.credentials
        # URLのパラメータをクリアしてリダイレクト（任意）
        st.query_params.clear()
        return build("calendar", "v3", credentials=flow.credentials)

    # ログインボタンを表示
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    st.markdown("### 🔐 Googleログインが必要です")
    st.link_button("👉 ここをタップしてログイン", auth_url)
    st.stop()

def get_month_range(year, month):
    start = datetime.datetime(year, month, 1)
    end = start + relativedelta(months=1)
    return start.isoformat() + 'Z', end.isoformat() + 'Z'

def calculate_salary(year, month):
    service = get_service()
    time_min, time_max = get_month_range(year, month)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    job_hours = {job: 0 for job in PARTTIME_JOBS.keys()}
    job_days = {job: 0 for job in PARTTIME_JOBS.keys()}
    job_koma = {job: 0 for job in PARTTIME_JOBS.keys()}

    for event in events:
        if 'summary' not in event or 'dateTime' not in event['start']:
            continue

        for job in PARTTIME_JOBS.keys():
            if job in event['summary']:
                start = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                end = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                
                hours = (end - start).total_seconds() / 3600
                job_hours[job] += hours
                job_days[job] += 1

                if job == "早稲アカ":
                    for _, k_start, k_end in WASEDA_KOMA:
                        k_s = start.replace(hour=int(k_start.split(":")[0]), minute=int(k_start.split(":")[1]))
                        k_e = start.replace(hour=int(k_end.split(":")[0]), minute=int(k_end.split(":")[1]))
                        if start < k_e and end > k_s:
                            job_koma[job] += 1

    job_salary = {}
    total_hours = 0
    total_salary = 0
    for job, hours in job_hours.items():
        wage = PARTTIME_JOBS[job]["wage"]
        calc_func = PARTTIME_JOBS[job]["calc_func"]
        salary = calc_func(hours, wage, job_days[job], job_koma[job]) if job == "早稲アカ" else calc_func(hours, wage, job_days[job])
        job_salary[job] = salary
        total_hours += hours
        total_salary += salary

    return job_hours, job_salary, job_koma, total_hours, total_salary
