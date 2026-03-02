import streamlit as st
import main
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import datetime

st.set_page_config(page_title="給料計算アプリ", layout="centered")

st.title("💰 給料計算アプリ")

# =========================
# 🔐 固定パスワード
# =========================
PASSWORD = "1234"

# =========================
# 年月スライド式変更
# =========================
# =========================
# 年月スライド式変更（左右対称修正版）
# =========================
if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date(2026, 2, 1)

col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    if st.button("◀", use_container_width=True):
        year = st.session_state.selected_date.year
        month = st.session_state.selected_date.month

        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1

        st.session_state.selected_date = datetime.date(year, month, 1)

with col_right:
    if st.button("▶", use_container_width=True):
        year = st.session_state.selected_date.year
        month = st.session_state.selected_date.month

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

        st.session_state.selected_date = datetime.date(year, month, 1)

with col_center:
    st.markdown(
        f"<h3 style='text-align:center'>{st.session_state.selected_date.year}年 "
        f"{st.session_state.selected_date.month}月</h3>",
        unsafe_allow_html=True
    )

year = st.session_state.selected_date.year
month = st.session_state.selected_date.month

st.divider()

# =========================
# 🔐 設定（時給変更）
# =========================
with st.expander("🔐 設定を開く"):

    password_input = st.text_input("パスワード", type="password")

    if password_input == PASSWORD:

        st.success("認証成功")
        st.subheader("時給変更")

        for job in main.PARTTIME_JOBS.keys():
            new_wage = st.number_input(
                f"{job} の時給",
                min_value=0,
                value=main.PARTTIME_JOBS[job]["wage"],
                step=10,
                key=f"wage_{job}"
            )
            main.PARTTIME_JOBS[job]["wage"] = new_wage

    elif password_input != "":
        st.error("パスワードが違います")

st.divider()

# =========================
# 🔵 強調ボタン
# =========================
col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])

with col_btn2:
    calculate_clicked = st.button("📊 計算する", use_container_width=True)

# =========================
# 計算処理
# =========================
if calculate_clicked:

    job_hours, job_salary, job_koma, total_hours, total_salary = main.calculate_salary(year, month)

    st.session_state["results"] = {
        "job_hours": job_hours,
        "job_salary": job_salary,
        "job_koma": job_koma,
        "total_hours": total_hours,
        "total_salary": total_salary,
        "expanded": True
    }

# =========================
# 結果表示
# =========================
if "results" in st.session_state:

    results = st.session_state["results"]

    st.header("📊 結果")

    # ===== バイト別 =====
    for job in main.PARTTIME_JOBS.keys():

        with st.expander(f"【{job}】", expanded=results["expanded"]):

            st.write(f"勤務時間: {results['job_hours'][job]:.2f} 時間")

            if job == "早稲アカ":
                st.write(f"コマ数: {results['job_koma'][job]}")

            st.write(f"給料: {results['job_salary'][job]:,.0f} 円")

    # ===== 総計 =====
    with st.expander("🧾 総計", expanded=results["expanded"]):

        col1, col2 = st.columns([1,1])

        with col1:
            st.metric("総勤務時間", f"{results['total_hours']:.2f} 時間")
            st.metric("総給料", f"{results['total_salary']:,.0f} 円")

        with col2:

            salaries_dict = results["job_salary"]

            if results["total_salary"] > 0:

                fig, ax = plt.subplots()

                # ===== Windows日本語フォント =====
                font_path = "C:/Windows/Fonts/msgothic.ttc"
                font_prop = fm.FontProperties(fname=font_path)

                # ===== 色指定 =====
                color_map = {
                    "早稲アカ": "#ff4500",
                    "とらや": "#008000",
                    "ハルエネ": "#9932cc"
                }

                labels = []
                salaries = []
                colors = []

                for job, salary in salaries_dict.items():
                    labels.append(job)
                    salaries.append(salary)
                    colors.append(color_map.get(job, "#cccccc"))

                wedges, texts, autotexts = ax.pie(
                    salaries,
                    labels=labels,
                    colors=colors,
                    autopct="%1.1f%%",
                    startangle=90
                )

                for text in texts:
                    text.set_fontproperties(font_prop)

                for autotext in autotexts:
                    autotext.set_fontproperties(font_prop)

                ax.set_title("給料割合", fontproperties=font_prop)

                st.pyplot(fig)

            else:
                st.info("データがありません")

    # 初回のみ展開、その後折り畳み可能
    st.session_state["results"]["expanded"] = True