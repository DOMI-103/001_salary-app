import streamlit as st
import main
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # 追加
import datetime
# 日本語フォント対策（OSに依存しない方法）
from matplotlib import rcParams
# Streamlit Cloud (Linux) で標準的な日本語フォントを指定
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

st.set_page_config(page_title="給料計算アプリ", layout="centered")
st.title("💰 給料計算アプリ")

PASSWORD = "1234"

# ===== 年月選択UI =====
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date(2026, 2, 1)

col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    if st.button("◀", use_container_width=True):
        d = st.session_state.selected_date
        st.session_state.selected_date = (d.replace(day=1) - datetime.timedelta(days=1)).replace(day=1)

with col_right:
    if st.button("▶", use_container_width=True):
        d = st.session_state.selected_date
        st.session_state.selected_date = (d.replace(day=28) + datetime.timedelta(days=5)).replace(day=1)

with col_center:
    st.markdown(f"<h3 style='text-align:center'>{st.session_state.selected_date.year}年 {st.session_state.selected_date.month}月</h3>", unsafe_allow_html=True)

year = st.session_state.selected_date.year
month = st.session_state.selected_date.month
st.divider()

# ===== 設定（時給変更） =====
with st.expander("🔐 設定を開く"):
    password_input = st.text_input("パスワード", type="password")
    if password_input == PASSWORD:
        st.success("認証成功")
        for job in main.PARTTIME_JOBS.keys():
            main.PARTTIME_JOBS[job]["wage"] = st.number_input(f"{job} の時給", min_value=0, value=main.PARTTIME_JOBS[job]["wage"], step=10, key=f"wage_{job}")
    elif password_input != "":
        st.error("パスワードが違います")

st.divider()

# ===== 計算実行 =====
if st.button("📊 計算する", type="primary", use_container_width=True):
    res = main.calculate_salary(year, month)
    st.session_state["results"] = {
        "job_hours": res[0], "job_salary": res[1], "job_koma": res[2],
        "total_hours": res[3], "total_salary": res[4], "expanded": True
    }

# ===== 結果表示 =====
if "results" in st.session_state:
    results = st.session_state["results"]
    st.header("📊 結果")

    for job in main.PARTTIME_JOBS.keys():
        with st.expander(f"【{job}】", expanded=results["expanded"]):
            st.write(f"勤務時間: {results['job_hours'][job]:.2f} 時間")
            if job == "早稲アカ":
                st.write(f"コマ数: {results['job_koma'][job]}")
            st.write(f"給料: {results['job_salary'][job]:,.0f} 円")

    with st.expander("🧾 総計", expanded=results["expanded"]):
        c1, c2 = st.columns([1, 1])
        with c1:
            st.metric("総勤務時間", f"{results['total_hours']:.2f} h")
            st.metric("総給料", f"{results['total_salary']:,.0f} 円")
        with c2:
            if results["total_salary"] > 0:
                # --- フォント設定 ---
                # GitHubにアップロードしたフォントファイルの名前を指定
                font_path = "MSGOTHIC.ttc" 
                
                # ファイルが存在する場合のみ適用
                if os.path.exists(font_path):
                    prop = fm.FontProperties(fname=font_path)
                else:
                    prop = None # フォントがない場合はデフォルト
                fig, ax = plt.subplots(figsize=(4, 4))
                color_map = {"早稲アカ": "#ff4500", "とらや": "#008000", "ハルエネ": "#9932cc"}
                labels = list(results["job_salary"].keys())
                values = list(results["job_salary"].values())
                colors = [color_map.get(j, "#cccccc") for j in labels]
                ax.pie(values, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
                ax.set_title("給料割合", fontsize=10)
                st.pyplot(fig)



