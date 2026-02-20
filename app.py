import streamlit as st
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Electricity Bill X-Ray (Jordan)", layout="centered")

st.title("⚡ Electricity Bill X-Ray – Jordan")
st.write("Estimate your household electricity bill based on real Jordan tariffs.")

# ===========================
# USER INPUTS
# ===========================

monthly_kwh = st.number_input("Monthly Consumption (kWh)", min_value=0, value=400)

ac_hours = st.slider("AC Usage (hours per day)", 0, 12, 6)
# Estimate AC consumption (assume average 1 kW AC)
ac_monthly_kwh = ac_hours * 30  # 1 kW × hours/day × 30 days


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
# OUTPUT
# ===========================

st.write("## 💰 Estimated Monthly Bill")
st.success(f"{estimated_bill:.2f} JOD")

st.write("## ❄️ AC Impact Analysis")

st.write(f"Estimated AC consumption: **{ac_monthly_kwh} kWh/month**")

ac_percentage = (ac_monthly_kwh / monthly_kwh) * 100 if monthly_kwh > 0 else 0

st.write(f"AC represents approximately **{ac_percentage:.1f}%** of your total consumption.")
#----------------------------------------------

st.write("### Tariff Used:")
st.write(tariff_type)

st.write("##  Bill Breakdown")

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

st.write("## 🛠 Savings Actions (Realistic)")

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

savings_jod = estimated_bill - new_bill

st.write(f"✅ New consumption: **{new_kwh} kWh**")
st.write(f"✅ New estimated bill: **{new_bill:.2f} JOD**")
st.success(f"💡 Estimated savings: **{savings_jod:.2f} JOD/month**")

st.write("##  Savings Simulator")

reduction = st.selectbox("If you reduce your consumption by:", ["5%", "10%", "20%"])
reduction_map = {"5%": 0.05, "10%": 0.10, "20%": 0.20}
r = reduction_map[reduction]

new_kwh = int(monthly_kwh * (1 - r))

if tariff_type == "Residential Supported":
    new_bill, _ = calculate_supported_bill(new_kwh)
else:
    new_bill, _ = calculate_non_supported_bill(new_kwh)

savings = estimated_bill - new_bill

st.write(f"✅ New consumption: **{new_kwh} kWh**")
st.write(f"✅ New estimated bill: **{new_bill:.2f} JOD**")
st.success(f"💡 Estimated savings: **{savings:.2f} JOD/month**")