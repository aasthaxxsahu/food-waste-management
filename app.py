import streamlit as st
import pandas as pd

from db_connection import get_connection

# -----------------------------------
# PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Food Waste Management Dashboard",
    layout="wide"
)

st.title("🍲 Food Waste Management Dashboard")

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

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------

st.sidebar.header("Filters")

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

# -----------------------------------
# DASHBOARD METRICS
# -----------------------------------

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

# -----------------------------------
# FOOD LISTINGS
# -----------------------------------

st.subheader("Food Listings")

st.write(
    f"Records Found: {len(filtered_df)}"
)

st.dataframe(
    filtered_df,
    use_container_width=True
)

# -----------------------------------
# PROVIDER CONTACT INFORMATION
# -----------------------------------

st.subheader("Provider Contact Information")

st.dataframe(
    filtered_providers,
    use_container_width=True
)

# -----------------------------------
# RECEIVER CONTACT INFORMATION
# -----------------------------------

st.subheader("Receiver Contact Information")

st.dataframe(
    receivers_df,
    use_container_width=True
)
# -----------------------------------
# CLAIMS INFORMATION
# -----------------------------------

st.subheader("Claims Information")

st.dataframe(
    claims_df,
    use_container_width=True
)

# =====================================
# SQL QUERY OUTPUTS
# =====================================

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
# CHART SECTION
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