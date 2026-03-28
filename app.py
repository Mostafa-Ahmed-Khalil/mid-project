
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Restaurant Sales Dashboard", layout="wide")

st.title("Restaurant Sales Dashboard")

# Load data
try:
    df = pd.read_csv('data/cleaned_restaurant_sales_data.csv')
except Exception as e:
    st.error(f"Error loading data: {e}")
    df = pd.DataFrame()

if df.empty:
    st.warning("No data available to display.")
else:
    df_filtered = df.copy()

    # --- Navigation ---
    page = st.sidebar.radio("Navigation", ["Dashboard", "Raw Data Preview", "Insights & Next Steps"])
    st.sidebar.markdown("---")

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    if 'order_year' in df_filtered.columns:
        years = sorted(df_filtered['order_year'].unique().tolist())
        selected_years = st.sidebar.multiselect("Select Year", years, default=years)
        if selected_years:
            df_filtered = df_filtered[df_filtered['order_year'].isin(selected_years)]

    if 'order_month' in df_filtered.columns:
        months = sorted(df_filtered['order_month'].unique().tolist())
        selected_months = st.sidebar.multiselect("Select Month", months, default=months)
        if selected_months:
            df_filtered = df_filtered[df_filtered['order_month'].isin(selected_months)]

    if 'category' in df_filtered.columns:
        categories = df_filtered['category'].unique().tolist()
        selected_categories = st.sidebar.multiselect("Select Categories", categories, default=categories)
        if selected_categories:
            df_filtered = df_filtered[df_filtered['category'].isin(selected_categories)]

    if 'order_day_name' in df_filtered.columns:
        days = df_filtered['order_day_name'].unique().tolist()
        selected_days = st.sidebar.multiselect("Select Days of Week", days, default=days)
        if selected_days:
            df_filtered = df_filtered[df_filtered['order_day_name'].isin(selected_days)]


    # --- Display Page Content ---
    if page == "Dashboard":
        # Top level metrics
        st.markdown("### Key Metrics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_revenue = df_filtered['order_total'].sum() if 'order_total' in df_filtered.columns else 0
            st.metric("Total Revenue", f"${total_revenue:,.2f}")

        with col2:
            total_orders = len(df_filtered)
            st.metric("Total Orders", f"{total_orders:,}")

        with col3:
            avg_order_value = df_filtered['order_total'].mean() if 'order_total' in df_filtered.columns else 0
            st.metric("Avg Order Value", f"${avg_order_value:,.2f}")

        with col4:
            total_items = df_filtered['quantity'].sum() if 'quantity' in df_filtered.columns else 0
            st.metric("Total Items Sold", f"{total_items:,.0f}")

        st.markdown("---")

        # Visualizations
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            if 'order_year' in df_filtered.columns and 'order_month' in df_filtered.columns and 'order_total' in df_filtered.columns:
                st.subheader("Monthly Revenue Trend")

                df_filtered['year_month'] = df_filtered['order_year'].astype(str) + '-' + df_filtered['order_month'].astype(str).str.zfill(2)

                monthly_sales = df_filtered.groupby('year_month')['order_total'].sum().reset_index()
                monthly_sales = monthly_sales.sort_values('year_month')

                fig1 = px.line(monthly_sales, x='year_month', y='order_total', 
                              labels={'year_month': 'Month', 'order_total': 'Total Sales ($)'},
                              markers=True)
                st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            if 'category' in df_filtered.columns and 'order_total' in df_filtered.columns:
                st.subheader("Sales by Category")
                category_sales = df_filtered.groupby('category')['order_total'].sum().reset_index()
                fig2 = px.pie(category_sales, values='order_total', names='category', hole=0.4)
                st.plotly_chart(fig2, use_container_width=True)

        col_chart3, col_chart4 = st.columns(2)

        with col_chart3:
            if 'order_day_name' in df_filtered.columns and 'order_total' in df_filtered.columns:
                st.subheader("Revenue by Day of the Week")

                # Order the days logically instead of alphabetically
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_sales = df_filtered.groupby('order_day_name')['order_total'].sum().reset_index()

                fig3 = px.bar(day_sales, x='order_day_name', y='order_total',
                             labels={'order_day_name': 'Day of Week', 'order_total': 'Total Sales ($)'},
                             color='order_day_name',
                             category_orders={'order_day_name': day_order})

                st.plotly_chart(fig3, use_container_width=True)

            elif 'payment_method' in df_filtered.columns:
                st.subheader("Payment Methods")
                payment_counts = df_filtered['payment_method'].value_counts().reset_index()
                payment_counts.columns = ['payment_method', 'count']
                fig3 = px.bar(payment_counts, x='payment_method', y='count',
                             labels={'payment_method': 'Payment Method', 'count': 'Number of Orders'},
                             color='payment_method')
                st.plotly_chart(fig3, use_container_width=True)

        with col_chart4:
            if 'item' in df_filtered.columns and 'quantity' in df_filtered.columns:
                st.subheader("Top Selling Items")
                top_items = df_filtered.groupby('item')['quantity'].sum().reset_index().sort_values('quantity', ascending=False).head(10)
                fig4 = px.bar(top_items, x='quantity', y='item', orientation='h',
                             labels={'quantity': 'Quantity Sold', 'item': 'Item'},
                             color='quantity', color_continuous_scale='Blues')
                fig4.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig4, use_container_width=True)

    elif page == "Raw Data Preview":
        st.subheader("Raw Data Preview")

        preview_df = df_filtered.drop(columns=['year_month']) if 'year_month' in df_filtered.columns else df_filtered

        st.dataframe(preview_df, use_container_width=True)

    elif page == "Insights & Next Steps":
        st.subheader("💡 Insights & Next Steps")

        st.markdown("""
### 1. Data Insights

#### Analysis: Distribution of Price
**1. Central Tendency:**
* **Median ($5.0):**
    * The median price of an item ordered is $5.0; so the half of the items sold cost less than $5, and half cost more.
    * This is also the highest peak (mode) in the histogram, indicating it's the most common price point.

**2. Data Spreed (Box Plot Insites)**
* **Overall Range:** Item prices range from a minimum of `$1.0` up to a maximum of `$20.0`.
* **IQR:** The middle 50% of the item prices fall tightly between `$4.0` (Q1) and `$7.0` (Q3).

**3. Shape of Distribution:**
* **Right-Skewed:** The data is heavily right-skewed. The vast majority of sales are concentrated on lower-priced items (under $10), with a long "tail" extending to the right.

**4. Outliers Analysis:**
* The box plot's upper fence is at `$10.0`. Any prices above this are considered statistical outliers within this dataset.
* We can observe distinct outlier clusters at approximately `$12`, `$14`, `$15`, `$18`, and `$20`. These higher-priced items likely represent premium main dishes or large combination meals, which are ordered less frequently than cheaper typical items like sides or beverages.

#### Analysis: Distribution of Item Quantities
**1. Central Tendency:**
* **Median (3):**
    * The median number of items ordered is exactly 3.
    * This sits perfectly in the middle of our data range, indicating a very balanced distribution.

**2. Data Spread (Box Plot Insights):**
* **Overall Range:** The quantity of items ordered in this dataset ranges strictly from a minimum of `1` to a maximum of `5`.
* **IQR:** The middle 50% of the data falls cleanly between `2` (Q1) and `4` (Q3). 

**3. Shape of Distribution:**
* **Uniform Distribution:** This histogram is flat. Customers are almost equally likely to order 1, 2, 3, 4, or 5 items in a single order. There is only a very marginal peak at a quantity of 3.

**4. Outliers Analysis:**
* **No Outliers:** The box plot reveals absolutely zero statistical outliers. The data is perfectly constrained between the minimum and maximum boundaries. This strongly suggests that there is a strict system limit enforcing a maximum of 5 identical items per order, or at least one per item per order.

#### Analysis: Distribution of Total Price per Order
**1. Central Tendency:**
* **Median ($15):**
    * The median total price of an order is `$15`.
    * Also it is the largest single peak (mode) in the histogram right around this value. This means half of all orders total less than $15, and half total more.

**2. Data Spread (Box Plot Insights):**
* **Overall Range:** Total order values span from a minimum of `$1` to a maximum of `$100`.
* **IQR:** The middle 50% of the revenue per order falls between `$8` (Q1) and `$24` (Q3). This `$8 to $24` range represents the "typical" order size for most customers.

**3. Shape of Distribution:**
* **Right-Skewed:** A long right tail pulls the distribution outwards to much higher order totals.

**4. Outliers Analysis:**
* **Upper Fence:** The box plot sets the upper fence at `$48`. Statistically, any single order totaling more than $48 is considered an outlier in this dataset.
* **Significant Outliers:** We see several outliers extending up to the maximum of `$100`. Noticeably, there is an artificial-looking spike exactly at `$60`, and another at the `$100` mark. These specific price points might correspond to set party bundles, other non most repeatative events.

---

### 2. Business Requirements & Next Steps
Based on our exploratory data analysis, the following business actions and requirements are recommended:

* **Review the 5-Item Quantity Limit:** The strict limit of 5 items per order is highly likely a technical constraint within the ordering system. **Action Required:** Discuss with the technical team to consider increasing this limit to capture larger group sizes.
* **Promote Premium Items:** High-priced items ($12-$20) exhibit outlier traits, meaning they are rarely ordered. **Action Required:** Introduce combo meals or promotional discounts targeting these premium dishes to boost their adoption.
* **Formalize Party Bundles:** The unusual spikes in order totals at exactly $60 and $100 suggest the occurrence of bulk custom orders. **Action Required:** Productize formal catering or "Party Bundles" priced around $60 and $100 to market explicitly to larger groups.
* **Marketing Focus on $5 Sweet Spot:** The most common item price is exactly $5.0. **Action Required:** Use this price point strategically in advertising to attract cost-conscious customers with a visible "Starting at $5" banner.
        """)
