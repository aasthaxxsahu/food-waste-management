import streamlit as st
import pandas as pd
import plotly.express as px

from db_connection import get_connection

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Food Waste Management Dashboard",
    layout="wide"
)

st.markdown("""
# 🥗 Local Food Waste Management System

### Connecting Surplus Food Providers to Those in Need
---
""")

st.markdown("""
<style>
div[data-testid="metric-container"] {
    background-color: #E8F5E9;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #2E7D32;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# DATABASE CONNECTION
# -----------------------------------

conn = get_connection()

food_df = pd.read_sql(
    "SELECT * FROM food_listings",
    conn
)

providers_df = pd.read_sql(
    "SELECT * FROM providers",
    conn
)

receivers_df = pd.read_sql(
    "SELECT * FROM receivers",
    conn
)

claims_df = pd.read_sql(
    "SELECT * FROM claims",
    conn
)
st.sidebar.title("🥗 Food Waste")

st.sidebar.success("Navigation Menu")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📊 SQL Queries",
        "📈 Charts",
        "🔍 Filter Search",
        "✏️ CRUD",
        "📋 Data Tables"
    ]
)

st.sidebar.markdown("---")

city = st.sidebar.selectbox(
    "Select City",
    ["All"] + sorted(food_df["Location"].unique().tolist())
)

provider_type = st.sidebar.selectbox(
    "Provider Type",
    ["All"] + sorted(food_df["Provider_Type"].unique().tolist())
)

food_type = st.sidebar.selectbox(
    "Food Type",
    ["All"] + sorted(food_df["Food_Type"].unique().tolist())
)

meal_type = st.sidebar.selectbox(
    "Meal Type",
    ["All"] + sorted(food_df["Meal_Type"].unique().tolist())
)

# -----------------------------------
# APPLY FILTERS
# -----------------------------------

filtered_df = food_df.copy()

if city != "All":
    filtered_df = filtered_df[
        filtered_df["Location"] == city
    ]

if provider_type != "All":
    filtered_df = filtered_df[
        filtered_df["Provider_Type"] == provider_type
    ]

if food_type != "All":
    filtered_df = filtered_df[
        filtered_df["Food_Type"] == food_type
    ]

if meal_type != "All":
    filtered_df = filtered_df[
        filtered_df["Meal_Type"] == meal_type
    ]

# -----------------------------------
# FILTERED PROVIDERS
# -----------------------------------

provider_ids = filtered_df["Provider_ID"].unique()

filtered_providers = providers_df[
    providers_df["Provider_ID"].isin(provider_ids)
]


if page == "🏠 Dashboard":
    
    total_food = food_df["Quantity"].sum()

    completed_claims = len(
        claims_df[claims_df["Status"] == "Completed"]
    )

    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric("🏪 Providers", len(providers_df))
    col2.metric("🤝 Receivers", len(receivers_df))
    col3.metric("🍱 Listings", len(food_df))
    col4.metric("📋 Claims", len(claims_df))
    col5.metric("📦 Total Qty", total_food)
    col6.metric("✅ Completed", completed_claims)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Filtered Listings",
            len(filtered_df)
        )

    with col2:
        st.metric(
            "Unique Providers",
            filtered_df["Provider_ID"].nunique()
        )

    with col3:
        st.metric(
            "Total Receivers",
            len(receivers_df)
        )

    with col4:
        st.metric(
            "Total Claims",
            len(claims_df)
        )

    st.header("📊 Dashboard Overview")

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Food Type Distribution")

    food_type_chart = (
        food_df["Food_Type"]
        .value_counts()
        .reset_index()
    )

    food_type_chart.columns = [
        "Food_Type",
        "Count"
    ]

    fig = px.pie(
        food_type_chart,
        names="Food_Type",
        values="Count",
        hole=0.4
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    with colB:
        st.subheader("Meal Type Distribution")

        st.bar_chart(
            food_df["Meal_Type"].value_counts()
        )

    colC, colD = st.columns(2)

    with colC:
        st.subheader("Provider Type Distribution")

        st.bar_chart(
            food_df["Provider_Type"].value_counts()
        )

    with colD:
        st.subheader("Top 10 Cities")

        st.bar_chart(
            food_df["Location"].value_counts().head(10)
        )


# =====================================
# SQL QUERY OUTPUTS
# =====================================

if page == "📊 SQL Queries":
    st.header("📊 SQL Query Outputs")

query_options = {
    "1. Providers by City":
    """
    SELECT City, COUNT(*) AS Providers_Count
    FROM providers
    GROUP BY City
    ORDER BY Providers_Count DESC
    LIMIT 10
    """,

    "2. Receivers by City":
    """
    SELECT City, COUNT(*) AS Receivers_Count
    FROM receivers
    GROUP BY City
    ORDER BY Receivers_Count DESC
    LIMIT 10
    """,

    "3. Provider Type Contributing Most Food":
    """
    SELECT Provider_Type,
           SUM(Quantity) AS Total_Food_Quantity
    FROM food_listings
    GROUP BY Provider_Type
    ORDER BY Total_Food_Quantity DESC
    """,

    "4. Food Providers Contact Information":
    """
    SELECT Provider_ID, Name, Contact, City
    FROM providers
    LIMIT 20
    """,

    "5. Receivers Claiming Most Food":
    """
    SELECT r.Receiver_ID,
           r.Name,
           COUNT(c.Claim_ID) AS Total_Claims
    FROM receivers r
    JOIN claims c
    ON r.Receiver_ID = c.Receiver_ID
    GROUP BY r.Receiver_ID,r.Name
    ORDER BY Total_Claims DESC
    LIMIT 10
    """,

    "6. Total Food Available":
    """
    SELECT SUM(Quantity) AS Total_Food_Available
    FROM food_listings
    """,

    "7. City with Highest Food Listings":
    """
    SELECT Location,
           COUNT(*) AS Food_Listings_Count
    FROM food_listings
    GROUP BY Location
    ORDER BY Food_Listings_Count DESC
    LIMIT 10
    """,

    "8. Most Common Food Type":
    """
    SELECT Food_Type,
           COUNT(*) AS Available_Count
    FROM food_listings
    GROUP BY Food_Type
    ORDER BY Available_Count DESC
    """,

    "9. Claims Per Food Item":
    """
    SELECT f.Food_ID,
           f.Food_Name,
           COUNT(c.Claim_ID) AS Total_Claims
    FROM food_listings f
    LEFT JOIN claims c
    ON f.Food_ID = c.Food_ID
    GROUP BY f.Food_ID,f.Food_Name
    ORDER BY Total_Claims DESC
    LIMIT 10
    """,

    "10. Provider with Most Successful Claims":
    """
    SELECT p.Provider_ID,
           p.Name,
           COUNT(c.Claim_ID) AS Successful_Claims
    FROM providers p
    JOIN food_listings f
    ON p.Provider_ID=f.Provider_ID
    JOIN claims c
    ON f.Food_ID=c.Food_ID
    WHERE c.Status='Completed'
    GROUP BY p.Provider_ID,p.Name
    ORDER BY Successful_Claims DESC
    LIMIT 10
    """,

    "11. Claim Status Percentage":
    """
    SELECT Status,
           COUNT(*) AS Total_Claims
    FROM claims
    GROUP BY Status
    """,

    "12. Average Quantity Claimed":
    """
    SELECT r.Receiver_ID,
           r.Name,
           ROUND(AVG(f.Quantity),2) AS Avg_Quantity
    FROM receivers r
    JOIN claims c
    ON r.Receiver_ID=c.Receiver_ID
    JOIN food_listings f
    ON c.Food_ID=f.Food_ID
    GROUP BY r.Receiver_ID,r.Name
    ORDER BY Avg_Quantity DESC
    LIMIT 10
    """,

    "13. Most Claimed Meal Type":
    """
    SELECT f.Meal_Type,
           COUNT(c.Claim_ID) AS Total_Claims
    FROM food_listings f
    JOIN claims c
    ON f.Food_ID=c.Food_ID
    GROUP BY f.Meal_Type
    ORDER BY Total_Claims DESC
    """,

    "14. Total Food Donated By Provider":
    """
    SELECT p.Provider_ID,
           p.Name,
           SUM(f.Quantity) AS Total_Donated
    FROM providers p
    JOIN food_listings f
    ON p.Provider_ID=f.Provider_ID
    GROUP BY p.Provider_ID,p.Name
    ORDER BY Total_Donated DESC
    LIMIT 10
    """,

    "15. Cities with Highest Demand":
    """
    SELECT r.City,
           COUNT(c.Claim_ID) AS Completed_Claims
    FROM receivers r
    JOIN claims c
    ON r.Receiver_ID=c.Receiver_ID
    WHERE c.Status='Completed'
    GROUP BY r.City
    ORDER BY Completed_Claims DESC
    LIMIT 10
    """
}

selected_query = st.selectbox(
    "Choose Query",
    list(query_options.keys())
)

query_result = pd.read_sql(
    query_options[selected_query],
    conn
)

st.dataframe(
    query_result,
    use_container_width=True
)
# =====================================
# CHART SECTION
# =====================================

if page == "📈 Charts":

    st.header("📈 Charts")

    chart_option = st.selectbox(
        "Select Chart",
        [
            "Food Type Distribution",
            "Meal Type Distribution",
            "Provider Type Distribution",
            "Food Listings by City"
        ]
    )

    if chart_option == "Food Type Distribution":

        chart_df = food_df["Food_Type"].value_counts()

        st.bar_chart(chart_df)

    elif chart_option == "Meal Type Distribution":

        chart_df = food_df["Meal_Type"].value_counts()

        st.bar_chart(chart_df)

    elif chart_option == "Provider Type Distribution":

        chart_df = food_df["Provider_Type"].value_counts()

        st.bar_chart(chart_df)

    elif chart_option == "Food Listings by City":

        chart_df = food_df["Location"].value_counts().head(10)

        st.bar_chart(chart_df)

# =====================================
# CRUD OPERATIONS
# =====================================

if page == "✏️ CRUD":
    st.header("✏️ CRUD Operations")

crud_option = st.selectbox(
    "Choose Operation",
    ["Create", "Update", "Delete"]
)

cursor = conn.cursor()

# CREATE
if crud_option == "Create":

    st.subheader("Add New Food Listing")

    food_id = st.number_input("Food ID", min_value=1)

    food_name = st.text_input("Food Name")

    quantity = st.number_input(
        "Quantity",
        min_value=1,
        step=1
    )

    expiry_date = st.date_input("Expiry Date")

    provider_id = st.number_input(
        "Provider ID",
        min_value=1,
        step=1
    )

    provider_type = st.text_input("Provider Type")

    location = st.text_input("Location")

    food_type = st.text_input("Food Type")

    meal_type = st.selectbox(
        "Meal Type",
        ["Breakfast", "Lunch", "Dinner", "Snacks"]
    )

    if st.button("Add Food Listing"):

        cursor.execute(
            """
            INSERT INTO food_listings
            (
                Food_ID,
                Food_Name,
                Quantity,
                Expiry_Date,
                Provider_ID,
                Provider_Type,
                Location,
                Food_Type,
                Meal_Type
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                food_id,
                food_name,
                quantity,
                expiry_date,
                provider_id,
                provider_type,
                location,
                food_type,
                meal_type
            )
        )

        conn.commit()

        st.success("Food Listing Added Successfully")

# UPDATE
elif crud_option == "Update":

    st.subheader("Update Food Quantity")

    update_id = st.number_input(
        "Food ID",
        min_value=1,
        step=1
    )

    new_quantity = st.number_input(
        "New Quantity",
        min_value=1,
        step=1
    )

    if st.button("Update Food Listing"):

        cursor.execute(
            """
            UPDATE food_listings
            SET Quantity=%s
            WHERE Food_ID=%s
            """,
            (
                new_quantity,
                update_id
            )
        )

        conn.commit()

        st.success("Food Listing Updated Successfully")

# DELETE
elif crud_option == "Delete":

    st.subheader("Delete Food Listing")

    delete_id = st.number_input(
        "Food ID to Delete",
        min_value=1,
        step=1
    )

    if st.button("Delete Food Listing"):

        cursor.execute(
            """
            DELETE FROM food_listings
            WHERE Food_ID=%s
            """,
            (delete_id,)
        )

        conn.commit()

        st.success("Food Listing Deleted Successfully")
        
# =====================================
# DATA TABLES PAGE
# =====================================

if page == "📋 Data Tables":

    st.header("📋 Data Tables")

    st.subheader("Food Listings")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.subheader("Providers")

    st.dataframe(
        filtered_providers,
        use_container_width=True
    )

    st.subheader("Receivers")

    st.dataframe(
        receivers_df,
        use_container_width=True
    )

    st.subheader("Claims")

    st.dataframe(
        claims_df,
        use_container_width=True
    )        