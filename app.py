import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(page_title="Electricity Bill X-Ray (Jordan)", layout="centered")

st.title("⚡ Electricity Bill X-Ray – Jordan")
st.write("Estimate your household electricity bill based on real Jordan tariffs.")

# ===========================
# USER INPUTS
# ===========================

monthly_kwh = st.number_input("Average Monthly Consumption (kWh)", min_value=0, value=400)

ac_hours = st.slider("AC Usage (hours per day)", 0, 12, 6)
ac_monthly_kwh = ac_hours * 30  # 1 kW × hours/day × 30 days (simple estimate)

tariff_type = st.selectbox(
    "Tariff Type",
    ["Residential Supported", "Residential Non-Supported"]
)

# ===========================
# BILL CALCULATION
# ===========================

def calculate_supported_bill(kwh):
    bill = 0
    breakdown = []

    if kwh <= 300:
        cost = kwh * 0.050
        bill += cost
        breakdown.append((kwh, 0.050, cost))

    elif kwh <= 600:
        cost1 = 300 * 0.050
        cost2 = (kwh - 300) * 0.100
        bill += cost1 + cost2
        breakdown.append((300, 0.050, cost1))
        breakdown.append((kwh - 300, 0.100, cost2))

    else:
        cost1 = 300 * 0.050
        cost2 = 300 * 0.100
        cost3 = (kwh - 600) * 0.200
        bill += cost1 + cost2 + cost3
        breakdown.append((300, 0.050, cost1))
        breakdown.append((300, 0.100, cost2))
        breakdown.append((kwh - 600, 0.200, cost3))

    return bill, breakdown

def calculate_non_supported_bill(kwh):
    bill = 0
    breakdown = []

    if kwh <= 1000:
        cost = kwh * 0.120
        bill += cost
        breakdown.append((kwh, 0.120, cost))
    else:
        cost1 = 1000 * 0.120
        cost2 = (kwh - 1000) * 0.150
        bill += cost1 + cost2
        breakdown.append((1000, 0.120, cost1))
        breakdown.append((kwh - 1000, 0.150, cost2))

    return bill, breakdown

def get_tier_warning(tariff_type, kwh):
    if tariff_type == "Residential Supported":
        if kwh <= 300:
            return "🟢 You are in the cheapest tier (1–300 kWh)."
        elif kwh <= 600:
            return "🟡 You entered the 301–600 kWh tier (higher price)."
        else:
            return "🔴 You are above 600 kWh (highest price tier). Consider reducing consumption."
    else:
        if kwh <= 1000:
            return "🟢 You are within 1–1000 kWh tier."
        else:
            return "🔴 You are above 1000 kWh (higher price tier). Consider reducing consumption."

# ===========================
# APPLY CALCULATION
# ===========================

if tariff_type == "Residential Supported":
    estimated_bill, breakdown = calculate_supported_bill(monthly_kwh)
else:
    estimated_bill, breakdown = calculate_non_supported_bill(monthly_kwh)

st.info(get_tier_warning(tariff_type, monthly_kwh))

# ===========================
# OUTPUT: BILL
# ===========================

st.write("## 💰 Estimated Monthly Bill")
st.success(f"{estimated_bill:.2f} JOD")

# ===========================
# AC IMPACT
# ===========================

st.write("## ❄️ AC Impact Analysis")
st.write(f"Estimated AC consumption: **{ac_monthly_kwh} kWh/month**")
ac_percentage = (ac_monthly_kwh / monthly_kwh) * 100 if monthly_kwh > 0 else 0
st.write(f"AC represents approximately **{ac_percentage:.1f}%** of your total consumption.")

# ===========================

# ===========================
# BILL BREAKDOWN
# ===========================

st.write("### Tariff Used:")
st.write(tariff_type)

st.write("## Bill Breakdown")
for kwh_used, rate, cost in breakdown:
    st.write(f"{kwh_used} kWh × {rate:.3f} JOD = {cost:.2f} JOD")

st.write("## Breakdown Table & Chart")
df = pd.DataFrame(breakdown, columns=["kWh in Tier", "Rate (JOD/kWh)", "Cost (JOD)"])
st.dataframe(df, use_container_width=True)

fig, ax = plt.subplots()
ax.bar(range(len(df)), df["Cost (JOD)"])
ax.set_xticks(range(len(df)))
ax.set_xticklabels([f"Tier {i+1}" for i in range(len(df))])
ax.set_ylabel("Cost (JOD)")
ax.set_title("Cost Contribution by Tier")
st.pyplot(fig)

# ===========================
# SAVINGS ACTIONS
# ===========================

st.write("## 🛠 Savings Actions")

action = st.selectbox(
    "Choose an action to simulate:",
    [
        "Reduce AC usage by 1 hour/day (~30 kWh/month)",
        "Reduce AC usage by 2 hours/day (~60 kWh/month)",
        "Use water heater timer (~40 kWh/month)",
        "Replace all bulbs with LED (~15 kWh/month)",
        "Unplug standby devices (~10 kWh/month)"
    ]
)

action_kwh_savings = {
    "Reduce AC usage by 1 hour/day (~30 kWh/month)": 30,
    "Reduce AC usage by 2 hours/day (~60 kWh/month)": 60,
    "Use water heater timer (~40 kWh/month)": 40,
    "Replace all bulbs with LED (~15 kWh/month)": 15,
    "Unplug standby devices (~10 kWh/month)": 10
}

saved_kwh = action_kwh_savings[action]
new_kwh = max(0, int(monthly_kwh - saved_kwh))

if tariff_type == "Residential Supported":
    new_bill, _ = calculate_supported_bill(new_kwh)
else:
    new_bill, _ = calculate_non_supported_bill(new_kwh)

action_savings_jod = estimated_bill - new_bill

st.write(f"✅ New consumption: **{new_kwh} kWh**")
st.write(f"✅ New estimated bill: **{new_bill:.2f} JOD**")
st.success(f"💡 Estimated savings: **{action_savings_jod:.2f} JOD/month**")

# ===========================
# % SAVINGS SIMULATOR
# ===========================

st.write("## Savings Simulator")

reduction = st.selectbox("If you reduce your consumption by:", ["5%", "10%", "20%"])
reduction_map = {"5%": 0.05, "10%": 0.10, "20%": 0.20}
r = reduction_map[reduction]

new_kwh2 = int(monthly_kwh * (1 - r))

if tariff_type == "Residential Supported":
    new_bill2, _ = calculate_supported_bill(new_kwh2)
else:
    new_bill2, _ = calculate_non_supported_bill(new_kwh2)

savings2 = estimated_bill - new_bill2

st.write(f"✅ New consumption: **{new_kwh2} kWh**")
st.write(f"✅ New estimated bill: **{new_bill2:.2f} JOD**")
st.success(f"💡 Estimated savings: **{savings2:.2f} JOD/month**")



# PV SYSTEM + ROOF CHECK
# ===========================

st.write("## ☀️ PV System")

use_pv = st.checkbox("Add PV system to offset my household bill")

if use_pv:
    # Project assumptions (Amman/Khalda)
    psh = 5.711
    derate = 0.7721
    panel_watt = 540

    offset_percent = st.slider("How much of your consumption should PV cover? (%)", 10, 100) / 100

    pv_kwp = (monthly_kwh * offset_percent) / (psh * 30 * derate)
    num_panels = math.ceil((pv_kwp * 1000) / panel_watt)
    pv_monthly_kwh = pv_kwp * psh * 30 * derate

    billed_kwh_after_pv = max(0, monthly_kwh - pv_monthly_kwh)

    if tariff_type == "Residential Supported":
        bill_after_pv, _ = calculate_supported_bill(billed_kwh_after_pv)
    else:
        bill_after_pv, _ = calculate_non_supported_bill(billed_kwh_after_pv)

    pv_savings_jod = estimated_bill - bill_after_pv

    st.write("### ✅ PV results")
    st.success(f"PV size needed: **{pv_kwp:.2f} kWp**")
    st.success(f"Estimated panels: **{num_panels} panels** (≈ {panel_watt} W each)")
    st.info(f"Estimated PV generation: **{pv_monthly_kwh:.0f} kWh/month**")
    st.write(f"New billed consumption: **{billed_kwh_after_pv:.0f} kWh/month**")
    st.write(f"New estimated bill: **{bill_after_pv:.2f} JOD/month**")
    st.success(f"Estimated savings: **{pv_savings_jod:.2f} JOD/month**")

    # ---- Roof check (NOW num_panels exists)
    st.write("### 🏠 Roof check (optional)")
    roof_area = st.number_input("Available roof area (m²)", min_value=0.0, value=30.0, step=1.0)
    usable_factor = st.slider("Usable roof factor (shading, spacing, obstacles)", 0.50, 1.00, 0.80, 0.01)
    panel_area = st.number_input("Panel area (m²) (typical 540W ≈ 2.6 m²)", min_value=1.0, value=2.6, step=0.1)

    required_area = num_panels * panel_area
    usable_roof_area = roof_area * usable_factor

    st.write(f"Estimated required panel area: **{required_area:.1f} m²**")
    st.write(f"Usable roof area: **{usable_roof_area:.1f} m²**")

    if required_area <= usable_roof_area:
        st.success("✅ Roof area looks sufficient for the estimated number of panels.")
    else:
        shortage = required_area - usable_roof_area
        st.warning(f"⚠️ Roof area may be insufficient by about **{shortage:.1f} m²**. Consider higher-watt panels, less offset %, or another roof section.")
