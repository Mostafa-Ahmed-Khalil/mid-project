
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(page_title="Restaurant Sales Dashboard", layout="wide")

# Title
st.title("🍽️ Restaurant Sales Dashboard")

# Load data directly
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
    page = st.sidebar.radio("Navigation", ["Dashboard", "Raw Data Preview"])
    st.sidebar.markdown("---")

    # --- Sidebar Filters ---
    st.sidebar.header("Filters")

    # Year Filter
    if 'order_year' in df_filtered.columns:
        years = sorted(df_filtered['order_year'].dropna().unique().tolist())
        selected_years = st.sidebar.multiselect("Select Year", years, default=years)
        if selected_years:
            df_filtered = df_filtered[df_filtered['order_year'].isin(selected_years)]

    # Month Filter
    if 'order_month' in df_filtered.columns:
        months = sorted(df_filtered['order_month'].dropna().unique().tolist())
        selected_months = st.sidebar.multiselect("Select Month", months, default=months)
        if selected_months:
            df_filtered = df_filtered[df_filtered['order_month'].isin(selected_months)]

    # Category Filter
    if 'category' in df_filtered.columns:
        categories = df_filtered['category'].dropna().unique().tolist()
        selected_categories = st.sidebar.multiselect("Select Categories", categories, default=categories)
        if selected_categories:
            df_filtered = df_filtered[df_filtered['category'].isin(selected_categories)]

    # Day of Week Filter
    if 'order_day_name' in df_filtered.columns:
        days = df_filtered['order_day_name'].dropna().unique().tolist()
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

                # Create a Year-Month string for plotting
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

        # Drop the temporary 'year_month' column from preview if it exists
        preview_df = df_filtered.drop(columns=['year_month']) if 'year_month' in df_filtered.columns else df_filtered

        # Display the whole filtered dataframe rather than just the head since it's on its own page
        st.dataframe(preview_df, use_container_width=True)
