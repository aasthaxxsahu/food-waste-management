import streamlit as st
import pandas as pd
import plotly.express as px

from db_connection import get_connection

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# GLOBAL CSS
# =====================================================

st.markdown("""
<style>

section[data-testid="stSidebar"] {
    background-color: #1B4332;
}
section[data-testid="stSidebar"] * {
    color: #F1F8F4 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

div[data-testid="stMetric"] {
    background-color: #E8F5E9;
    padding: 18px 16px;
    border-radius: 12px;
    border-left: 6px solid #2E7D32;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
div[data-testid="stMetricLabel"] {
    font-weight: 600;
    color: #1B4332 !important;
}
div[data-testid="stMetricValue"] {
    color: #2E7D32 !important;
}

.section-pill {
    background-color: #E8F5E9;
    color: #1B4332;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 10px;
}

.contact-card {
    background-color: #F1F8F4;
    border: 1px solid #C8E6C9;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.contact-card a {
    color: #2E7D32;
    font-weight: 600;
    text-decoration: none;
}

h1, h2, h3 {
    color: #1B4332;
}
hr {
    margin: 0.5rem 0 1.5rem 0;
}

</style>
""", unsafe_allow_html=True)

PALETTE = ["#2E7D32", "#66BB6A", "#A5D6A7", "#FF8A65",
           "#4DB6AC", "#9575CD", "#FFB74D", "#4FC3F7"]


def section_header(label: str):
    st.markdown(f'<div class="section-pill">{label}</div>', unsafe_allow_html=True)


def render_contact_card(name, role, contact, city=None):
    """Render a contact card with clickable mailto/tel links so users
    can reach providers/receivers directly from the app."""
    contact = str(contact) if contact is not None else ""
    is_email = "@" in contact
    link = f"mailto:{contact}" if is_email else f"tel:{contact}"
    icon = "📧" if is_email else "📞"

    city_html = f"<br><small>📍 {city}</small>" if city else ""

    st.markdown(
        f"""
        <div class="contact-card">
            <b>{name}</b> &nbsp;<span style="opacity:0.7;">({role})</span><br>
            {icon} <a href="{link}">{contact}</a>
            {city_html}
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================================
# HERO
# =====================================================

st.markdown("""
# 🥗 Local Food Wastage Management System
*Connecting surplus food providers with those in need*
---
""")

# =====================================================
# DATABASE CONNECTION + DATA LOAD
# =====================================================

conn = get_connection()


@st.cache_data(ttl=300)
def load_data():
    food = pd.read_sql("SELECT * FROM food_listings", conn)
    providers = pd.read_sql("SELECT * FROM providers", conn)
    receivers = pd.read_sql("SELECT * FROM receivers", conn)
    claims = pd.read_sql("SELECT * FROM claims", conn)
    return food, providers, receivers, claims


food_df, providers_df, receivers_df, claims_df = load_data()

RECEIVERS_HAVE_CONTACT = "Contact" in receivers_df.columns

# =====================================================
# SIDEBAR — NAVIGATION + FILTERS
# =====================================================

st.sidebar.markdown("## 🥗 Food Wastage")
st.sidebar.markdown("##### Management System")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Go to:",
    [
        "🏠 Dashboard",
        "📊 SQL Queries (15)",
        "📈 EDA & Charts",
        "🔍 Filter & Search",
        "📞 Contact Directory",
        "✏️ CRUD Operations",
        "📋 Data Tables"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Global Filters")

city = st.sidebar.selectbox(
    "City",
    ["All"] + sorted(food_df["Location"].dropna().unique().tolist())
)

provider_name = st.sidebar.selectbox(
    "Provider",
    ["All"] + sorted(
        providers_df["Name"].dropna().unique().tolist()
    ) if "Name" in providers_df.columns else ["All"]
)

food_type = st.sidebar.selectbox(
    "Food Type",
    ["All"] + sorted(food_df["Food_Type"].dropna().unique().tolist())
)

meal_type = st.sidebar.selectbox(
    "Meal Type",
    ["All"] + sorted(food_df["Meal_Type"].dropna().unique().tolist())
)

st.sidebar.markdown("---")
st.sidebar.caption("Python · SQL · Streamlit · Plotly")

# =====================================================
# APPLY FILTERS
# =====================================================

filtered_df = food_df.copy()

if city != "All":
    filtered_df = filtered_df[filtered_df["Location"] == city]

if provider_name != "All" and "Name" in providers_df.columns:
    matching_provider_ids = providers_df.loc[
        providers_df["Name"] == provider_name, "Provider_ID"
    ].tolist()
    filtered_df = filtered_df[filtered_df["Provider_ID"].isin(matching_provider_ids)]

if food_type != "All":
    filtered_df = filtered_df[filtered_df["Food_Type"] == food_type]

if meal_type != "All":
    filtered_df = filtered_df[filtered_df["Meal_Type"] == meal_type]

provider_ids = filtered_df["Provider_ID"].unique()
filtered_providers = providers_df[providers_df["Provider_ID"].isin(provider_ids)]


# =====================================================
# PAGE: DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    total_food = food_df["Quantity"].sum()
    completed_claims = len(claims_df[claims_df["Status"] == "Completed"])

    st.markdown("## 📈 Food Wastage & Donation Analytics")
    st.caption("Real-time metrics pulled via targeted SQL analysis queries.")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🏪 Providers", f"{len(providers_df):,}")
    col2.metric("🤝 Receivers", f"{len(receivers_df):,}")
    col3.metric("🍱 Listings", f"{len(food_df):,}")
    col4.metric("📋 Claims", f"{len(claims_df):,}")
    col5.metric("📦 Total Qty", f"{total_food:,}")
    col6.metric("✅ Completed", f"{completed_claims:,}")

    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Filtered Listings", len(filtered_df))
    with col2:
        st.metric("Unique Providers", filtered_df["Provider_ID"].nunique())
    with col3:
        st.metric("Total Receivers", len(receivers_df))
    with col4:
        st.metric("Total Claims", len(claims_df))

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        section_header("🏆 Top Contributing Food Providers")
        top_providers = (
            food_df.groupby("Provider_ID")["Quantity"]
            .sum()
            .reset_index()
            .merge(providers_df[["Provider_ID", "Name"]], on="Provider_ID", how="left")
            .sort_values("Quantity", ascending=False)
            .head(10)
        )
        fig = px.bar(
            top_providers, x="Name", y="Quantity", color="Name",
            color_discrete_sequence=PALETTE,
            labels={"Quantity": "Quantity (Units)", "Name": ""}
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with colB:
        section_header("✅ Claim Status Breakdown")
        status_counts = claims_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(
            status_counts, names="Status", values="Count",
            hole=0.45, color_discrete_sequence=PALETTE
        )
        fig.update_traces(textinfo="label+percent")
        st.plotly_chart(fig, use_container_width=True)

    colC, colD = st.columns(2)

    with colC:
        section_header("🍽️ Food Type Distribution")
        food_type_chart = food_df["Food_Type"].value_counts().reset_index()
        food_type_chart.columns = ["Food_Type", "Count"]
        fig = px.pie(
            food_type_chart, names="Food_Type", values="Count",
            hole=0.4, color_discrete_sequence=PALETTE
        )
        st.plotly_chart(fig, use_container_width=True)

    with colD:
        section_header("🕐 Meal Type Distribution")
        meal_chart = food_df["Meal_Type"].value_counts().reset_index()
        meal_chart.columns = ["Meal_Type", "Count"]
        fig = px.bar(
            meal_chart, x="Meal_Type", y="Count", color="Meal_Type",
            color_discrete_sequence=PALETTE
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    colE, colF = st.columns(2)

    with colE:
        section_header("🏪 Provider Type Distribution")
        provider_type_chart = food_df["Provider_Type"].value_counts().reset_index()
        provider_type_chart.columns = ["Provider_Type", "Count"]
        fig = px.bar(
            provider_type_chart, x="Provider_Type", y="Count", color="Provider_Type",
            color_discrete_sequence=PALETTE
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with colF:
        section_header("🌆 Top 10 Cities by Listings")
        city_chart = food_df["Location"].value_counts().head(10).reset_index()
        city_chart.columns = ["Location", "Count"]
        fig = px.bar(
            city_chart, x="Location", y="Count", color="Location",
            color_discrete_sequence=PALETTE
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)


# =====================================================
# PAGE: SQL QUERIES (ALL 15)
# =====================================================

elif page == "📊 SQL Queries (15)":

    st.markdown("## 📊 SQL Query Outputs")
    st.caption("All 15 analysis queries, run live against the database.")

    query_options = {
        "1. Providers by City": """
            SELECT City, COUNT(*) AS Providers_Count
            FROM providers
            GROUP BY City
            ORDER BY Providers_Count DESC
            LIMIT 10
        """,
        "2. Receivers by City": """
            SELECT City, COUNT(*) AS Receivers_Count
            FROM receivers
            GROUP BY City
            ORDER BY Receivers_Count DESC
            LIMIT 10
        """,
        "3. Provider Type Contributing Most Food": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Food_Quantity
            FROM food_listings
            GROUP BY Provider_Type
            ORDER BY Total_Food_Quantity DESC
        """,
        "4. Food Providers Contact Information": """
            SELECT Provider_ID, Name, Contact, City
            FROM providers
            LIMIT 20
        """,
        "5. Receivers Claiming Most Food": """
            SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Receiver_ID, r.Name
            ORDER BY Total_Claims DESC
            LIMIT 10
        """,
        "6. Total Food Available": """
            SELECT SUM(Quantity) AS Total_Food_Available
            FROM food_listings
        """,
        "7. City with Highest Food Listings": """
            SELECT Location, COUNT(*) AS Food_Listings_Count
            FROM food_listings
            GROUP BY Location
            ORDER BY Food_Listings_Count DESC
            LIMIT 10
        """,
        "8. Most Common Food Type": """
            SELECT Food_Type, COUNT(*) AS Available_Count
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Available_Count DESC
        """,
        "9. Claims Per Food Item": """
            SELECT f.Food_ID, f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM food_listings f
            LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_ID, f.Food_Name
            ORDER BY Total_Claims DESC
            LIMIT 10
        """,
        "10. Provider with Most Successful Claims": """
            SELECT p.Provider_ID, p.Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID, p.Name
            ORDER BY Successful_Claims DESC
            LIMIT 10
        """,
        "11. Claim Status Percentage": """
            SELECT Status, COUNT(*) AS Total_Claims
            FROM claims
            GROUP BY Status
        """,
        "12. Average Quantity Claimed": """
            SELECT r.Receiver_ID, r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY r.Receiver_ID, r.Name
            ORDER BY Avg_Quantity DESC
            LIMIT 10
        """,
        "13. Most Claimed Meal Type": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM food_listings f
            JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Total_Claims DESC
        """,
        "14. Total Food Donated By Provider": """
            SELECT p.Provider_ID, p.Name, SUM(f.Quantity) AS Total_Donated
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Provider_ID, p.Name
            ORDER BY Total_Donated DESC
            LIMIT 10
        """,
        "15. Cities with Highest Demand": """
            SELECT r.City, COUNT(c.Claim_ID) AS Completed_Claims
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            WHERE c.Status = 'Completed'
            GROUP BY r.City
            ORDER BY Completed_Claims DESC
            LIMIT 10
        """,
    }

    st.markdown("##### Run an individual query")
    selected_query = st.selectbox("Choose Query", list(query_options.keys()))
    query_result = pd.read_sql(query_options[selected_query], conn)
    st.dataframe(query_result, use_container_width=True)

    numeric_cols = query_result.select_dtypes(include="number").columns.tolist()
    text_cols = query_result.select_dtypes(exclude="number").columns.tolist()
    if numeric_cols and text_cols and len(query_result) <= 20:
        section_header("📊 Visualized Result")
        fig = px.bar(
            query_result, x=text_cols[0], y=numeric_cols[0], color=text_cols[0],
            color_discrete_sequence=PALETTE
        )
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    with st.expander("📂 View ALL 15 query outputs at once"):
        for label, sql in query_options.items():
            st.markdown(f"**{label}**")
            st.code(sql.strip(), language="sql")
            result = pd.read_sql(sql, conn)
            st.dataframe(result, use_container_width=True)
            st.markdown("---")


# =====================================================
# PAGE: EDA & CHARTS
# =====================================================

elif page == "📈 EDA & Charts":

    st.markdown("## 📈 EDA & Charts")

    chart_option = st.selectbox(
        "Select Chart",
        [
            "Food Type Distribution",
            "Meal Type Distribution",
            "Provider Type Distribution",
            "Food Listings by City",
            "Claim Status Breakdown",
            "Quantity Distribution"
        ]
    )

    if chart_option == "Food Type Distribution":
        chart_df = food_df["Food_Type"].value_counts().reset_index()
        chart_df.columns = ["Food_Type", "Count"]
        fig = px.bar(chart_df, x="Food_Type", y="Count",
                     color="Food_Type", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Meal Type Distribution":
        chart_df = food_df["Meal_Type"].value_counts().reset_index()
        chart_df.columns = ["Meal_Type", "Count"]
        fig = px.bar(chart_df, x="Meal_Type", y="Count",
                     color="Meal_Type", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Provider Type Distribution":
        chart_df = food_df["Provider_Type"].value_counts().reset_index()
        chart_df.columns = ["Provider_Type", "Count"]
        fig = px.bar(chart_df, x="Provider_Type", y="Count",
                     color="Provider_Type", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Food Listings by City":
        chart_df = food_df["Location"].value_counts().head(10).reset_index()
        chart_df.columns = ["Location", "Count"]
        fig = px.bar(chart_df, x="Location", y="Count",
                     color="Location", color_discrete_sequence=PALETTE)
        fig.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Claim Status Breakdown":
        chart_df = claims_df["Status"].value_counts().reset_index()
        chart_df.columns = ["Status", "Count"]
        fig = px.pie(chart_df, names="Status", values="Count",
                     hole=0.45, color_discrete_sequence=PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_option == "Quantity Distribution":
        fig = px.histogram(food_df, x="Quantity", nbins=30,
                            color_discrete_sequence=[PALETTE[0]])
        st.plotly_chart(fig, use_container_width=True)


# =====================================================
# PAGE: FILTER & SEARCH
# =====================================================

elif page == "🔍 Filter & Search":

    st.markdown("## 🔍 Filter & Search Listings")
    st.caption("Results reflect the City / Provider / Food Type / Meal Type filters in the sidebar.")

    st.markdown(f"**{len(filtered_df)} listings found**")
    st.dataframe(filtered_df, use_container_width=True)

    section_header("🏪 Matching Providers")
    st.dataframe(filtered_providers, use_container_width=True)


# =====================================================
# PAGE: CONTACT DIRECTORY  (providers + receivers, clickable)
# =====================================================

elif page == "📞 Contact Directory":

    st.markdown("## 📞 Contact Directory")
    st.caption("Reach providers and receivers directly — click an email to open your mail app, or a phone number to call.")

    tab1, tab2 = st.tabs(["🏪 Providers", "🤝 Receivers"])

    with tab1:
        search_p = st.text_input("Search providers by name or city", key="search_providers")

        providers_view = filtered_providers if len(filtered_providers) > 0 else providers_df

        if search_p:
            mask = pd.Series(False, index=providers_view.index)
            if "Name" in providers_view.columns:
                mask |= providers_view["Name"].astype(str).str.contains(search_p, case=False, na=False)
            if "City" in providers_view.columns:
                mask |= providers_view["City"].astype(str).str.contains(search_p, case=False, na=False)
            providers_view = providers_view[mask]

        if len(providers_view) == 0:
            st.info("No providers match this search.")
        else:
            for _, row in providers_view.iterrows():
                render_contact_card(
                    name=row.get("Name", "Unknown"),
                    role="Provider",
                    contact=row.get("Contact", "N/A"),
                    city=row.get("City")
                )

    with tab2:
        if not RECEIVERS_HAVE_CONTACT:
            st.warning(
                "The `receivers` table doesn't have a `Contact` column in this database, "
                "so contact cards can't be shown. Add a `Contact` column to enable this."
            )
        else:
            search_r = st.text_input("Search receivers by name or city", key="search_receivers")

            receivers_view = receivers_df.copy()
            if search_r:
                mask = pd.Series(False, index=receivers_view.index)
                if "Name" in receivers_view.columns:
                    mask |= receivers_view["Name"].astype(str).str.contains(search_r, case=False, na=False)
                if "City" in receivers_view.columns:
                    mask |= receivers_view["City"].astype(str).str.contains(search_r, case=False, na=False)
                receivers_view = receivers_view[mask]

            if len(receivers_view) == 0:
                st.info("No receivers match this search.")
            else:
                for _, row in receivers_view.iterrows():
                    render_contact_card(
                        name=row.get("Name", "Unknown"),
                        role="Receiver",
                        contact=row.get("Contact", "N/A"),
                        city=row.get("City")
                    )


# =====================================================
# PAGE: CRUD OPERATIONS
# =====================================================

elif page == "✏️ CRUD Operations":

    st.markdown("## ✏️ CRUD Operations")

    crud_option = st.selectbox("Choose Operation", ["Create", "Update", "Delete"])

    cursor = conn.cursor()

    if crud_option == "Create":
        st.subheader("Add New Food Listing")

        c1, c2, c3 = st.columns(3)
        with c1:
            food_id = st.number_input("Food ID", min_value=1, step=1)
            quantity = st.number_input("Quantity", min_value=1, step=1)
            provider_id_in = st.number_input("Provider ID", min_value=1, step=1)
        with c2:
            food_name = st.text_input("Food Name")
            expiry_date = st.date_input("Expiry Date")
            provider_type_in = st.text_input("Provider Type")
        with c3:
            location_in = st.text_input("Location")
            food_type_in = st.text_input("Food Type")
            meal_type_in = st.selectbox(
                "Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"]
            )

        if st.button("➕ Add Food Listing", use_container_width=True):
            cursor.execute(
                """
                INSERT INTO food_listings
                (Food_ID, Food_Name, Quantity, Expiry_Date,
                 Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    food_id, food_name, quantity, expiry_date,
                    provider_id_in, provider_type_in, location_in,
                    food_type_in, meal_type_in
                )
            )
            conn.commit()
            st.success("✅ Food Listing Added Successfully")
            st.cache_data.clear()

    elif crud_option == "Update":
        st.subheader("Update Food Quantity")

        c1, c2 = st.columns(2)
        with c1:
            update_id = st.number_input("Food ID", min_value=1, step=1)
        with c2:
            new_quantity = st.number_input("New Quantity", min_value=1, step=1)

        if st.button("🔄 Update Food Listing", use_container_width=True):
            cursor.execute(
                "UPDATE food_listings SET Quantity=%s WHERE Food_ID=%s",
                (new_quantity, update_id)
            )
            conn.commit()
            st.success("✅ Food Listing Updated Successfully")
            st.cache_data.clear()

    elif crud_option == "Delete":
        st.subheader("Delete Food Listing")

        delete_id = st.number_input("Food ID to Delete", min_value=1, step=1)

        if st.button("🗑️ Delete Food Listing", use_container_width=True):
            cursor.execute(
                "DELETE FROM food_listings WHERE Food_ID=%s",
                (delete_id,)
            )
            conn.commit()
            st.success("✅ Food Listing Deleted Successfully")
            st.cache_data.clear()


# =====================================================
# PAGE: DATA TABLES
# =====================================================

elif page == "📋 Data Tables":

    st.markdown("## 📋 Data Tables")

    section_header("🍱 Food Listings")
    st.dataframe(filtered_df, use_container_width=True)

    section_header("🏪 Providers")
    st.dataframe(filtered_providers, use_container_width=True)

    section_header("🤝 Receivers")
    st.dataframe(receivers_df, use_container_width=True)

    section_header("📋 Claims")
    st.dataframe(claims_df, use_container_width=True)