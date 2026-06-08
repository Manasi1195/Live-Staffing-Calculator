import math
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st

st.set_page_config(page_title="Contact Center Staffing Calculator", layout="wide")

BELL = [0.30,0.50,0.70,0.90,1.00,1.10,1.20,1.15,1.10,1.00,0.90,0.80,
        0.75,0.70,0.65,0.60,0.55,0.50,0.45,0.40,0.35,0.30,0.25,0.20]

def erlang_c(N, A):
    if N <= A: return 1.0
    inv = 1.0
    for k in range(1, N + 1):
        inv = 1.0 + inv * k / A
    eb = 1.0 / inv
    return N * eb / (N - A * (1 - eb))

def service_level(N, A, T, aht):
    return 1.0 - erlang_c(N, A) * math.exp(-(N - A) * T / aht)

def avg_speed_of_answer(N, A, aht):
    return erlang_c(N, A) * aht / (N - A)

def min_agents(A, sl_pct, T, aht):
    N = max(math.ceil(A) + 1, 1)
    while service_level(N, A, T, aht) < sl_pct / 100:
        N += 1
        if N > 999: break
    return N

def run_calculation(aht, sl_target, answer_time, op_hours, shrinkage, daily_calls):
    start   = (24 - op_hours) // 2
    weights = BELL[start: start + op_hours]
    wsum    = sum(weights)
    calls_list = [round(daily_calls * w / wsum) for w in weights]
    labels = []
    for i in range(op_hours):
        h = start + i
        labels.append(f"{h % 12 or 12}:00 {'AM' if h < 12 else 'PM'}")
    rows = []
    for i, calls in enumerate(calls_list):
        if calls == 0:
            rows.append({"Hour": labels[i], "Calls": 0, "Erlangs": 0.0,
                         "Min Agents": 0, "Headcount": 0,
                         "Utilisation %": 0.0, "ASA (sec)": 0.0, "Service Level %": 100.0})
            continue
        A  = (calls / 3600) * aht
        N  = min_agents(A, sl_target, answer_time, aht)
        hc = math.ceil(N / (1 - shrinkage))
        rows.append({
            "Hour":            labels[i],
            "Calls":           calls,
            "Erlangs":         round(A, 2),
            "Min Agents":      N,
            "Headcount":       hc,
            "Utilisation %":   round(A / N * 100, 1),
            "ASA (sec)":       round(avg_speed_of_answer(N, A, aht), 1),
            "Service Level %": round(service_level(N, A, answer_time, aht) * 100, 1),
        })
    return pd.DataFrame(rows)


st.title("Contact Center Staffing Calculator")
st.caption("Erlang-C based agent requirement planner")

with st.sidebar:
    st.header("Input Parameters")
    aht         = st.slider("Average Handle Time — AHT (sec)", 30, 600, 240, 10)
    sl_target   = st.slider("Target Service Level (%)", 50, 99, 80)
    answer_time = st.slider("Target Answer Time (sec)", 5, 60, 20)
    op_hours    = st.slider("Operating Hours per Day", 4, 24, 12)
    shrinkage   = st.slider("Shrinkage (%)", 5, 50, 20)
    daily_calls = st.number_input("Total Daily Call Volume", min_value=1, max_value=100000, value=1200, step=100)
    st.divider()
    st.caption("Adjust any value — the dashboard updates instantly.")

shrinkage_dec = shrinkage / 100
df     = run_calculation(aht, sl_target, answer_time, op_hours, shrinkage_dec, daily_calls)
active = df[df["Calls"] > 0]

peak_hc  = int(df["Headcount"].max())
avg_sl   = active["Service Level %"].mean()
avg_asa  = active["ASA (sec)"].mean()
avg_util = active["Utilisation %"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Peak Headcount", peak_hc,        f"+{shrinkage}% shrinkage")
c2.metric("Avg Service Level", f"{avg_sl:.1f}%",   f"target {sl_target}%")
c3.metric("Avg Speed of Answer", f"{avg_asa:.0f}s")
c4.metric("Avg Utilisation",   f"{avg_util:.1f}%", "HIGH — review" if avg_util > 85 else "Healthy")

st.divider()

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    fig1.patch.set_facecolor("#f5f6fa")
    ax1.set_facecolor("#f5f6fa")
    x = range(len(df))
    ax1.bar([i - 0.2 for i in x], df["Headcount"],  width=0.38, color="#378ADD", label="Headcount (rostered)")
    ax1.bar([i + 0.2 for i in x], df["Min Agents"], width=0.38, color="#9FE1CB", label="Min Agents (Erlang-C)")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["Hour"], rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Agents")
    ax1.set_title("Intraday Staffing Requirements", fontweight="bold")
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", alpha=0.3)
    for sp in ax1.spines.values(): sp.set_color("#dde1ea")
    st.pyplot(fig1)
    plt.close(fig1)

with col_chart2:
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    fig2.patch.set_facecolor("#f5f6fa")
    ax2.set_facecolor("#f5f6fa")
    ax2b = ax2.twinx()
    ax2.bar(list(x), df["Calls"], color="#E8ECF5", label="Calls")
    ax2b.plot(list(x), df["Service Level %"], color="#185FA5", marker="o", markersize=5, linewidth=2, label="SL %")
    ax2b.axhline(sl_target, color="#E05A5A", linestyle="--", linewidth=1.5, label=f"Target ({sl_target}%)")
    ax2b.set_ylim(0, 115)
    ax2b.set_ylabel("Service Level %")
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(df["Hour"], rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("Call Volume")
    ax2.set_title("Call Volume vs Service Level", fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)
    for sp in ax2.spines.values(): sp.set_color("#dde1ea")
    l1, lb1 = ax2.get_legend_handles_labels()
    l2, lb2 = ax2b.get_legend_handles_labels()
    ax2.legend(l1 + l2, lb1 + lb2, fontsize=8, loc="upper left")
    st.pyplot(fig2)
    plt.close(fig2)

st.divider()
st.subheader("Intraday Staffing Breakdown")

def colour_row(row):
    sl  = row["Service Level %"]
    ut  = row["Utilisation %"]
    sl_colour = "background-color: #d4edda" if sl >= sl_target else "background-color: #f8d7da"
    ut_colour = "background-color: #fff3cd" if ut > 85 else ""
    return ["", "", "", "", "", ut_colour, "", sl_colour]

styled = (
    df.style
    .apply(colour_row, axis=1)
    .format({"Erlangs": "{:.2f}", "Utilisation %": "{:.1f}",
             "ASA (sec)": "{:.1f}", "Service Level %": "{:.1f}"})
)
st.dataframe(styled, use_container_width=True, hide_index=True)

with st.expander("How It Works"):
    st.markdown("""
**Step 1: Traffic Intensity (Erlangs)**
`A = (Calls per hour × AHT) / 3600`

**Step 2: Erlang-C: Call Wait Time**
`P(wait) = ErlangC(N, A)`
We try N = ceil(A)+1, N+1, N+2 ... until the service level target is met.

**Step 3: Service Level**
`SL = 1 − P(wait) × exp(−(N − A) × target_time / AHT)`

**Step 4: Average Speed of Answer**
`ASA = P(wait) × AHT / (N − A)`

**Step 5: Utilisation**
`Utilisation % = A / N × 100`   keeping below 85% to avoid queue build-up.

**Step 6: Headcount with Shrinkage**
`Headcount = ceil(N / (1 − shrinkage%))`
""")
