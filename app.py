import io
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration & High-End Styling
st.set_page_config(
    page_title="Fleet Operations & Captain Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; font-family: 'Inter', sans-serif; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.metric-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; padding: 20px;
        border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    h1, h2, h3 { color: #0F172A; font-weight: 700; }
    </style>
""",
    unsafe_allow_html=True,
)

# 2. Application Header
st.markdown(
    """
    <div style='padding: 1rem 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 2rem;'>
        <h1 style='color: #0F172A; font-size: 2.2rem; margin-bottom: 0;'>🚗 Fleet Operations Dashboard</h1>
        <p style='color: #64748B; font-size: 1.05rem;'>Real-time operational monitoring, captain status, and financial balance tracker.</p>
    </div>
""",
    unsafe_allow_html=True,
)


# 3. Fallback Sample Data Generator
@st.cache_data
def load_sample_data():
    data = {
        "captain_id": [101, 102, 103, 104, 105],
        "city": ["Amman", "Irbid", "Amman", "Zarqa", "Amman"],
        "captain_name": [
            "Ahmad Ali",
            "Omar Khaled",
            "Tariq Ziad",
            "Mohammed Nour",
            "Sami Youssef",
        ],
        "sex": ["M", "M", "M", "M", "M"],
        "phone_number": [
            "+962790000001",
            "+962780000002",
            "+962770000003",
            "+962791111111",
            "+962782222222",
        ],
        "captain_nid": [
            990111222,
            985222333,
            970333444,
            960444555,
            950555666,
        ],
        "join_date": [
            "2024-01-10",
            "2024-03-15",
            "2023-11-20",
            "2024-05-01",
            "2023-08-12",
        ],
        "last_trip_date": [
            "2026-09-20",
            "2026-09-19",
            "2026-09-21",
            "2026-09-10",
            "2026-09-21",
        ],
        "limo_company_name": [
            "Alpha Fleet",
            "Beta Limo",
            "Alpha Fleet",
            "Gamma Transit",
            "Beta Limo",
        ],
        "last_dct_id": [5001, 5002, 5003, 5004, 5005],
        "last_dct": ["Amman Airport", "City Center", "Sweifieh", "Zarqa Hub", "Abdali"],
        "limo_company_id": [10, 20, 10, 30, 20],
        "cumulative_trip_count": [1420, 850, 2300, 410, 1900],
        "tier": ["Gold", "Silver", "Platinum", "Bronze", "Platinum"],
        "captain_block_status": [
            "Active",
            "Active",
            "Active",
            "Blocked",
            "Active",
        ],
        "balance": [-15.50, 45.00, -120.00, 5.00, 230.50],
        "cash_block": ["No", "No", "Yes", "Yes", "No"],
        "blocking_cash_limit": [100.0, 100.0, 50.0, 50.0, 150.0],
        "warning_cash_limit": [75.0, 75.0, 30.0, 30.0, 100.0],
    }
    return pd.DataFrame(data)


# 4. Sidebar Data Input Section (Supports File Upload OR Direct Text Paste)
st.sidebar.markdown("### 📊 Data Management", unsafe_allow_html=True)
input_method = st.sidebar.radio(
    "Choose Input Method", ["Upload CSV File", "Paste CSV Data"]
)

df = None

if input_method == "Upload CSV File":
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV Export", type=["csv", "txt"]
    )
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {e}")
else:
    pasted_data = st.sidebar.text_area(
        "Paste CSV / Excel Data Here",
        placeholder=(
            "captain_id\tcity\tcaptain_name...\n(Include headers in the first"
            " row)"
        ),
        height=150,
    )
    if pasted_data:
        try:
            # Automatically sniffs delimiter whether comma-separated or tab-separated (Excel copy-paste)
            df = pd.read_csv(io.StringIO(pasted_data), sep=None, engine="python")
        except Exception as e:
            st.error(
                f"Could not parse data. Ensure headers are present. Error: {e}"
            )

# Fallback to sample data if nothing is uploaded or pasted yet
if df is None:
    df = load_sample_data()
    st.sidebar.info(
        "💡 Showing sample data. Upload a file or paste your dataset to view live"
        " metrics."
    )

# 5. Sidebar Global Filters
st.sidebar.markdown("### 🔍 Filters")
selected_cities = st.sidebar.multiselect(
    "Filter by City",
    options=df["city"].unique().tolist(),
    default=df["city"].unique().tolist(),
)
selected_companies = st.sidebar.multiselect(
    "Filter by Limo Company",
    options=df["limo_company_name"].unique().tolist(),
    default=df["limo_company_name"].unique().tolist(),
)
selected_statuses = st.sidebar.multiselect(
    "Captain Status",
    options=df["captain_block_status"].unique().tolist(),
    default=df["captain_block_status"].unique().tolist(),
)

# Apply Filters
filtered_df = df[
    (df["city"].isin(selected_cities))
    & (df["limo_company_name"].isin(selected_companies))
    & (df["captain_block_status"].isin(selected_statuses))
]

# 6. Top Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)
total_captains = len(filtered_df)
active_captains = len(
    filtered_df[filtered_df["captain_block_status"] == "Active"]
)
total_trips = filtered_df["cumulative_trip_count"].sum()
total_balance = filtered_df["balance"].sum()
cash_blocked_count = len(filtered_df[filtered_df["cash_block"] == "Yes"])

with col1:
    st.metric(
        label="Total Captains",
        value=f"{total_captains:,}",
        delta=f"{active_captains} Active",
    )
with col2:
    st.metric(label="Total Trips Count", value=f"{total_trips:,}")
with col3:
    st.metric(label="Net Wallet Balance", value=f"${total_balance:,.2f}")
with col4:
    st.metric(
        label="Cash Blocked", value=f"{cash_blocked_count}", delta="Needs review"
    )
with col5:
    avg_trips = (
        int(total_trips / total_captains) if total_captains > 0 else 0
    )
    st.metric(label="Avg Trips / Captain", value=f"{avg_trips:,}")

st.markdown("<br>", unsafe_allow_html=True)

# 7. Charts Row
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("### 🏆 Trips Distribution by Tier")
    if not filtered_df.empty:
        tier_df = (
            filtered_df.groupby("tier")["cumulative_trip_count"]
            .sum()
            .reset_index()
        )
        fig_tier = px.bar(
            tier_df,
            x="tier",
            y="cumulative_trip_count",
            color="tier",
            color_discrete_sequence=px.colors.sequential.Teal,
            template="plotly_white",
        )
        fig_tier.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_tier, use_container_width=True)

with chart_col2:
    st.markdown("### 🏢 Performance per Limo Company")
    if not filtered_df.empty:
        comp_df = (
            filtered_df.groupby("limo_company_name")["cumulative_trip_count"]
            .sum()
            .reset_index()
        )
        fig_comp = px.pie(
            comp_df,
            names="limo_company_name",
            values="cumulative_trip_count",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r,
            template="plotly_white",
        )
        fig_comp.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_comp, use_container_width=True)

# 8. Detailed Data Grid & Search
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📋 Detailed Captains Database")

search_query = st.text_input(
    "🔍 Quick Search Captain",
    placeholder="Type captain name, ID, or phone number...",
)
if search_query:
    filtered_df = filtered_df[
        filtered_df["captain_name"]
        .str.contains(search_query, case=False, na=False)
        | filtered_df["captain_id"].astype(str).str.contains(search_query)
        | filtered_df["phone_number"].astype(str).str.contains(search_query)
    ]

st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.download_button(
    label="📥 Export Filtered Data to CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_captain_metrics.csv",
    mime="text/csv",
)
