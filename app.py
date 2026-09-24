from datetime import datetime, time
import json
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Duty & Salary Tracker", page_icon="💰", layout="centered"
)

st.title("💰 Duty & Salary Tracker")
st.write(
    "Rozana ki timing enter karein. Backup save rakhne ke liye neeche download"
    " option use karein."
)

# Fixed Settings
MONTHLY_SALARY = 40000
WORKING_DAYS = 26
REGULAR_HOURS = 9
OVERTIME_RATE = 350
per_hour_rate = MONTHLY_SALARY / (WORKING_DAYS * REGULAR_HOURS)

# Initialize Session State
if "history" not in st.session_state:
  st.session_state.history = []

# --- SIDEBAR: Backup & Restore System ---
with st.sidebar:
  st.subheader("💾 Data Backup System")
  st.write(
      "Cloud server sleep hone par data mehfooz rakhne ke liye yahan se backup"
      " lein:"
  )

  # Export Backup (Download JSON)
  if st.session_state.history:
    json_data = json.dumps(st.session_state.history, indent=4)
    st.download_button(
        label="📤 Backup Download Karein",
        data=json_data,
        file_name="duty_backup.json",
        mime="application/json",
        use_container_width=True,
    )

  # Import Backup (Upload JSON)
  uploaded_file = st.file_uploader(
      "📥 Purana Backup Upload Karein", type=["json"]
  )
  if uploaded_file is not None:
    try:
      loaded_data = json.load(uploaded_file)
      if isinstance(loaded_data, list):
        st.session_state.history = loaded_data
        st.success("✅ Backup kamiyabi se load ho gaya!")
    except:
      st.error("❌ Ghalat file format!")

# --- MAIN FORM ---
with st.form("duty_entry_form"):
  entry_date = st.date_input(
      "Tarikh (Date)", value=datetime.today(), key="form_entry_date"
  )

  col1, col2 = st.columns(2)
  with col1:
    in_time_str = st.text_input(
        "Aane ka Waqt (In Time)", value="08:16 AM", key="form_in_time"
    )
  with col2:
    out_time_str = st.text_input(
        "Jane ka Waqt (Out Time)", value="05:50 PM", key="form_out_time"
    )

  submit_btn = st.form_submit_button(
      "🚀 Hisaab Karein aur Save Karein",
      use_container_width=True,
      key="form_submit_btn",
  )

if submit_btn:
  try:
    t_in = datetime.strptime(in_time_str.strip().upper(), "%I:%M %p").time()
    t_out = datetime.strptime(out_time_str.strip().upper(), "%I:%M %p").time()

    dt_in = datetime.combine(entry_date, t_in)
    dt_out = datetime.combine(entry_date, t_out)

    if dt_out <= dt_in:
      st.error(
          "❌ Ghalat Waqt: Jane ka waqt aane ke waqt ke baad ka hona chahiye!"
      )
    else:
      diff_seconds = (dt_out - dt_in).total_seconds()
      total_hours = diff_seconds / 3600

      if total_hours <= REGULAR_HOURS:
        reg_pay = total_hours * per_hour_rate
        ot_pay = 0
        ot_hours = 0
      else:
        reg_pay = REGULAR_HOURS * per_hour_rate
        ot_hours = total_hours - REGULAR_HOURS
        ot_pay = ot_hours * OVERTIME_RATE

      total_pay = reg_pay + ot_pay
      hrs = int(total_hours)
      mins = int(round((total_hours - hrs) * 60))

      entry_record = {
          "Date": entry_date.strftime("%Y-%m-%d"),
          "In": in_time_str.upper(),
          "Out": out_time_str.upper(),
          "Total Time": f"{hrs}h {mins}m",
          "Regular Pay": round(reg_pay, 2),
          "Overtime (PKR)": round(ot_pay, 2),
          "Total Earning": round(total_pay, 2),
      }

      current_history = [
          h for h in st.session_state.history if h["Date"] != str(entry_date)
      ]
      current_history.append(entry_record)
      st.session_state.history = sorted(
          current_history, key=lambda x: x["Date"], reverse=True
      )

      st.success("✅ Entry save ho gayi!")

      m1, m2 = st.columns(2)
      m1.metric(
          label="Aj ki Kul Kamai", value=f"PKR {round(total_pay, 2):,.2f}"
      )
      m2.metric(
          label="Duty Time",
          value=f"{hrs}h {mins}m",
          delta=f"+{ot_hours:.1f}h OT" if ot_hours > 0 else "On Time",
      )

  except ValueError:
    st.error(
        "⚠️ Waqt ka format theek likhein. Maslan: **08:16 AM** ya **05:50 PM**"
    )

# --- History Dashboard ---
if st.session_state.history:
  st.markdown("---")
  st.subheader("📊 Mahine ka Khulasa (Summary Dashboard)")

  df = pd.DataFrame(st.session_state.history)
  total_days_worked = len(df)
  total_earned_sum = df["Total Earning"].sum()

  c1, c2 = st.columns(2)
  c1.metric("Kul Din (Days Worked)", f"{total_days_worked} Din")
  c2.metric("Kul Earning (Total)", f"PKR {total_earned_sum:,.2f}")

  st.markdown("---")
  st.subheader("📅 Tafseeli Record (History Table)")
  st.dataframe(df, use_container_width=True)

  csv_data = df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Sara Record Excel (CSV) mein Download Karein",
      data=csv_data,
      file_name="duty_salary_record.csv",
      mime="text/csv",
      use_container_width=True,
      key="download_csv_btn",
  )

  if st.button(
      "🗑️ Sari History Clear Karein",
      use_container_width=True,
      type="secondary",
      key="clear_history_btn",
  ):
    st.session_state.history = []
    st.rerun()
