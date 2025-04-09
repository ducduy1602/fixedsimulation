
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

st.set_page_config(layout="wide")
st.title("📦 Conveyor Simulation & Animation App")

# --------------------
# Sidebar: User Inputs
# --------------------
st.sidebar.header("System Parameters")
input_rate = st.sidebar.slider("Tote Input Rate (totes/hour)", 60, 200, 131, step=1)
packer_count = st.sidebar.slider("Total Packing Tables", 10, 20, 13)
slow_tables = st.sidebar.slider("No. of Slow Tables (70% rate)", 0, packer_count, 3)
conveyor_length = st.sidebar.slider("Conveyor Length (m)", 5, 30, 15, step=1)
conveyor_speed = st.sidebar.number_input("Conveyor Speed (m/s)", value=4.0, step=0.1)
tote_length = st.sidebar.number_input("Tote Length (m)", value=0.6, step=0.1)

# Base rates
base_rate_per_table = 96 / 10
fast_tables = packer_count - slow_tables
packing_capacity = (fast_tables * base_rate_per_table) + (slow_tables * base_rate_per_table * 0.7)

# Derived calculations
capacity_shortfall = input_rate - packing_capacity
conveyor_capacity = int(conveyor_length // tote_length)
hours_until_overflow = conveyor_capacity / capacity_shortfall if capacity_shortfall > 0 else float('inf')
utilization = (packing_capacity / input_rate) * 100
pack_time = 3600 / packing_capacity
input_interval = 3600 / input_rate

# --------------------
# KPIs
# --------------------
st.subheader("📊 System KPIs")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Input Rate", f"{input_rate} totes/hr")
col2.metric("Packing Capacity", f"{packing_capacity:.2f} totes/hr")
col3.metric("Shortfall", f"{capacity_shortfall:.2f} totes/hr")
col4.metric("Hours Until Overflow", f"{hours_until_overflow:.2f}" if capacity_shortfall > 0 else "∞")

st.markdown("---")

# ----------------------------
# Conveyor Overflow Simulation
# ----------------------------
st.subheader("📈 Conveyor Buffer Fill-Up Over Time")
if capacity_shortfall > 0:
    hours = list(range(0, int(hours_until_overflow) + 2))
    totes_waiting = [min(h * capacity_shortfall, conveyor_capacity) for h in hours]
    df = pd.DataFrame({"Hour": hours, "Totes on Conveyor": totes_waiting})
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df["Hour"], df["Totes on Conveyor"], marker='o')
    ax.set_xlabel("Time (Hours)")
    ax.set_ylabel("Totes on Conveyor")
    ax.set_title("Conveyor Fill-Up Due to Capacity Shortfall")
    ax.grid(True)
    st.pyplot(fig)
else:
    st.success("✅ No overflow! Packing capacity exceeds input rate.")

st.markdown("---")

# --------------------
# Conveyor Animation
# --------------------
st.subheader("🎞️ Animated Conveyor")
animation_speed = st.slider("Animation Speed (slower ←→ faster)", 0.05, 1.0, 0.2, step=0.05)
num_totes = st.slider("Number of Totes on Conveyor", 1, 10, 5)
placeholder = st.empty()
num_cells = int(conveyor_length / tote_length)

def render_conveyor(positions, cells):
    line = []
    for i in range(cells):
        if i in positions:
            line.append("📦")
        else:
            line.append("—")
    return " ".join(line)

# Fixed animation logic
for step in range(num_cells + num_totes):
    current_positions = [
        step - i for i in range(num_totes)
        if 0 <= step - i < num_cells
    ]
    conveyor_line = render_conveyor(current_positions, num_cells)
    placeholder.markdown(f"### {conveyor_line}")
    time.sleep(animation_speed)
