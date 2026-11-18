import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Churn Retention Dashboard", layout="wide")
customers = pd.read_csv("outputs/dashboard_customers.csv").fillna("")
drivers = pd.read_csv("outputs/dashboard_drivers.csv")
agreement = pd.read_csv("outputs/shap_lime_agreement.csv")

st.title("Customer churn risk")
st.caption("Drivers shown are only those that both SHAP and LIME rank in their top 10.")

left, mid, right = st.columns(3)
bands = left.multiselect("Risk band", ["High", "Medium", "Low"], default=["High", "Medium"])
contracts = mid.multiselect("Contract", sorted(customers["Contract"].unique()),
                            default=sorted(customers["Contract"].unique()))
min_p = right.slider("Minimum churn probability", 0.0, 1.0, 0.0, 0.05)

view = customers[customers["risk_band"].isin(bands) & customers["Contract"].isin(contracts)
                 & (customers["churn_probability"] >= min_p)]

a, b, c = st.columns(3)
a.metric("Customers shown", f"{len(view):,}")
b.metric("Average churn probability", f"{view['churn_probability'].mean():.1%}" if len(view) else "n/a")
c.metric("High-risk customers", f"{(customers['risk_band'] == 'High').sum():,}")

st.subheader("Customers ranked by churn risk")
st.dataframe(view[["customerID", "churn_probability", "risk_band", "driver_1", "driver_2",
                   "driver_3", "Contract", "tenure", "MonthlyCharges"]],
             use_container_width=True, hide_index=True)

st.subheader("Customer detail")
if len(view):
    pick = st.selectbox("Customer", view["customerID"].tolist())
    row = customers[customers["customerID"] == pick].iloc[0]
    d1, d2 = st.columns(2)
    d1.metric("Churn probability", f"{row['churn_probability']:.1%}", row["risk_band"])
    shown = [row[k] for k in ["driver_1", "driver_2", "driver_3"] if row[k] != ""]
    d2.write("**Agreed drivers pushing this customer's risk up:**")
    d2.write(", ".join(shown) if shown else "No agreed driver increases this customer's risk.")

st.subheader("What drives churn overall")
g1, g2 = st.columns(2)
g1.bar_chart(drivers.head(10).set_index("variable")["shap_importance"])
g1.write("Agreed by SHAP and LIME: " + ", ".join(drivers.loc[drivers["agreed_top10"], "variable"]))
g2.dataframe(agreement, hide_index=True, use_container_width=True)