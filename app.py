from datetime import datetime, time
import pandas as pd
import streamlit as st
import streamlit_localstorage as st_lc

# Page Configuration
st.set_page_config(
    page_title="Permanent Duty Tracker", page_icon="⚡", layout="centered"
)

st.title("⚡ Permanent Duty & Salary Tracker")
st.write(
    "Yeh app aapke mobile ke browser mein data save karegi taake data kabhi na"
    " urre!"
)

# Initialize Browser Local Storage
localS = st_lc.LocalStorage()

# Fixed Settings
MONTHLY_SALARY = 40000
WORKING_DAYS = 26  # 4 chuttiyan nikal kar
REGULAR_HOURS = 9
OVERTIME_RATE = 350
per_hour_rate = MONTHLY_SALARY / (WORKING_DAYS * REGULAR_HOURS)

# Load history from Browser Local Storage into Session State
if "history" not in st.session_state:
  saved_data = localS.getItem("duty_history_permanent")
  if saved_data and isinstance(saved_data, list):
    st.session_state.history = saved_data
  else:
    st.session_state.history = []

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
    # 12-hour format parsing
    t_in = datetime.strptime(in_time_str.strip().upper(), "%I:%M %p").time()
    t_out = datetime.strptime(out_time_str.strip().upper(), "%I:%M %p").time()

    dt_in = datetime.combine(entry_date, t_in)
    dt_out = datetime.combine(entry_date, t_out)

    if dt_out <= dt_in:
      st.error(
          "❌ Ghalat Waqt: Jane ka waqt aane ke waqt ke baad ka hona chahiye!"
      )
    else:
      # Total duration in hours
      diff_seconds = (dt_out - dt_in).total_seconds()
      total_hours = diff_seconds / 3600

      # Regular vs Overtime calculation
      if total_hours <= REGULAR_HOURS:
        reg_pay = total_hours * per_hour_rate
        ot_pay = 0
        ot_hours = 0
      else:
        reg_pay = REGULAR_HOURS * per_hour_rate
        ot_hours = total_hours - REGULAR_HOURS
        ot_pay = ot_hours * OVERTIME_RATE

      total_pay = reg_pay + ot_pay

      # Format hours and minutes for display
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

      # Update or append entry
      current_history = [
          h for h in st.session_state.history if h["Date"] != str(entry_date)
      ]
      current_history.append(entry_record)

      st.session_state.history = sorted(
          current_history, key=lambda x: x["Date"], reverse=True
      )

      # **Permanent Save to Mobile Browser Storage**
      localS.setItem("duty_history_permanent", st.session_state.history)

      st.success("✅ Entry aapke mobile browser mein permanently save ho gayi!")

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

# --- Analytics & History Dashboard ---
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

  # Download Button for Excel/CSV
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
    localS.deleteItem("duty_history_permanent")
    st.rerun()
  return []


# Save history to file
def save_history(history_data):
  with open(DATA_FILE, "w") as f:
    json.dump(history_data, f, indent=4)


# Session State initialization from file
if "history" not in st.session_state:
  st.session_state.history = load_history()

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
    # 12-hour format parsing
    t_in = datetime.strptime(in_time_str.strip().upper(), "%I:%M %p").time()
    t_out = datetime.strptime(out_time_str.strip().upper(), "%I:%M %p").time()

    dt_in = datetime.combine(entry_date, t_in)
    dt_out = datetime.combine(entry_date, t_out)

    if dt_out <= dt_in:
      st.error(
          "❌ Ghalat Waqt: Jane ka waqt aane ke waqt ke baad ka hona chahiye!"
      )
    else:
      # Total duration in hours
      diff_seconds = (dt_out - dt_in).total_seconds()
      total_hours = diff_seconds / 3600

      # Regular vs Overtime calculation
      if total_hours <= REGULAR_HOURS:
        reg_pay = total_hours * per_hour_rate
        ot_pay = 0
        ot_hours = 0
      else:
        reg_pay = REGULAR_HOURS * per_hour_rate
        ot_hours = total_hours - REGULAR_HOURS
        ot_pay = ot_hours * OVERTIME_RATE

      total_pay = reg_pay + ot_pay

      # Format hours and minutes for display
      hrs = int(total_hours)
      mins = int(round((total_hours - hrs) * 60))

      # Save entry record dictionary
      entry_record = {
          "Date": entry_date.strftime("%Y-%m-%d"),
          "In": in_time_str.upper(),
          "Out": out_time_str.upper(),
          "Total Time": f"{hrs}h {mins}m",
          "Regular Pay": round(reg_pay, 2),
          "Overtime (PKR)": round(ot_pay, 2),
          "Total Earning": round(total_pay, 2),
      }

      # Purani list se is date ka record hata kar naya add karein
      current_history = [
          h for h in st.session_state.history if h["Date"] != str(entry_date)
      ]
      current_history.append(entry_record)

      # Sort history by date descending (newest first)
      st.session_state.history = sorted(
          current_history, key=lambda x: x["Date"], reverse=True
      )

      # Permanent file mein save karein
      save_history(st.session_state.history)

      st.success("✅ Entry kamiyabi se save ho gayi!")

      # Metric cards
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

# --- Analytics & History Dashboard ---
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

  # Download Button for Excel/CSV
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
    if os.path.exists(DATA_FILE):
      os.remove(DATA_FILE)
    st.rerun()
