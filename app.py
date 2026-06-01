import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page configuration ────────────────────────────────────────────────────────
# Must be the very first Streamlit call in the file.
# layout="wide" uses the full browser width instead of the default narrow column.
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
# Injects styles into the rendered page.
# We use this to style the KPI metric cards and general typography.
st.markdown("""
    <style>
        /* Remove default top padding so the header sits flush */
        .block-container { padding-top: 1.5rem; }

        /* KPI card: white box with subtle shadow */
        .kpi-card {
            background: #ffffff;
            border-radius: 12px;
            padding: 20px 24px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            border-left: 4px solid #4F8BF9;
        }
        .kpi-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.9rem;
            font-weight: 700;
            color: #111827;
            line-height: 1.1;
        }
        .kpi-sub {
            font-size: 0.8rem;
            color: #9ca3af;
            margin-top: 2px;
        }

        /* Sidebar background */
        [data-testid="stSidebar"] { background-color: #f8fafc; }

        /* Section headings */
        h2 { color: #111827; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
# @st.cache_data tells Streamlit to run this function ONCE and cache the result.
# Without it, the CSV would be re-read from disk on every user interaction,
# making the dashboard slow. The cache is cleared only when the file changes.
@st.cache_data
def load_data():
    df = pd.read_csv("orders_clean.csv", parse_dates=["order_date", "ship_date"])
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["order_year"]  = df["order_date"].dt.year
    df["ship_days"]   = (df["ship_date"] - df["order_date"]).dt.days
    return df

df = load_data()


# ── Sidebar: filters ──────────────────────────────────────────────────────────
# st.sidebar.* widgets appear in the collapsible left panel.
# Every widget returns its current value, which we store in variables
# and use to filter the dataframe before drawing any chart.
st.sidebar.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=52)
st.sidebar.markdown("## Filters")

# Date range slider
min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()
date_range = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# Multiselect filters — default is all options selected
all_cities      = sorted(df["city"].dropna().unique())
all_categories  = sorted(df["category"].dropna().unique())
all_statuses    = sorted(df["order_status"].dropna().unique())

cities     = st.sidebar.multiselect("City",           all_cities,     default=all_cities)
categories = st.sidebar.multiselect("Category",       all_categories, default=all_categories)
statuses   = st.sidebar.multiselect("Order Status",   all_statuses,   default=all_statuses)

st.sidebar.markdown("---")
st.sidebar.caption("Data: East Africa E-Commerce Orders · 2023–2025")


# ── Apply filters ─────────────────────────────────────────────────────────────
# Build a boolean mask from all active filters and apply it in one step.
# This creates a new dataframe `fdf` (filtered df) used by every chart below.
# The original `df` is never modified so filters can be freely changed.
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start, end = df["order_date"].min(), df["order_date"].max()

mask = (
    df["order_date"].between(start, end) &
    df["city"].isin(cities) &
    df["category"].isin(categories) &
    df["order_status"].isin(statuses)
)
fdf = df[mask].copy()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# E-Commerce Sales Dashboard")
st.markdown(
    f"Showing **{len(fdf):,}** orders from "
    f"**{start.strftime('%d %b %Y')}** to **{end.strftime('%d %b %Y')}**"
)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — KPI CARDS
# ══════════════════════════════════════════════════════════════════════════════
# st.columns(n) divides the row into n equal-width columns.
# We unpack them directly into named variables for clarity.

total_orders    = len(fdf)
total_revenue   = fdf["total_kes"].sum()
avg_order_value = fdf["total_kes"].mean()
avg_rating      = fdf["review_rating"].mean()
avg_ship_days   = fdf["ship_days"].dropna().mean()
top_city        = fdf["city"].value_counts().idxmax() if not fdf.empty else "—"

def kpi(label, value, sub=""):
    """Render a single KPI card using raw HTML for precise styling."""
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
    """, unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1: kpi("Total Orders",    f"{total_orders:,}")
with c2: kpi("Total Revenue",   f"KES {total_revenue/1e6:.1f}M")
with c3: kpi("Avg Order Value", f"KES {avg_order_value:,.0f}")
with c4: kpi("Avg Rating",      f"{avg_rating:.1f} / 5")
with c5: kpi("Avg Ship Days",   f"{avg_ship_days:.1f} days")
with c6: kpi("Top City",        top_city.title())

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — SALES TRENDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Sales Trends")

col_left, col_right = st.columns(2)

with col_left:
    # Group by month and sum revenue
    monthly_rev = (
        fdf.groupby("order_month")["total_kes"]
        .sum()
        .reset_index()
        .rename(columns={"order_month": "Month", "total_kes": "Revenue (KES)"})
    )
    fig = px.area(
        monthly_rev,
        x="Month", y="Revenue (KES)",
        title="Monthly Revenue (KES)",
        color_discrete_sequence=["#4F8BF9"],
    )
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=45, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        margin=dict(t=40, b=0, l=0, r=0),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    # Group by month and count orders
    monthly_orders = (
        fdf.groupby("order_month")["order_id"]
        .count()
        .reset_index()
        .rename(columns={"order_month": "Month", "order_id": "Orders"})
    )
    fig2 = px.bar(
        monthly_orders,
        x="Month", y="Orders",
        title="Monthly Order Volume",
        color_discrete_sequence=["#34D399"],
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(tickangle=45, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        margin=dict(t=40, b=0, l=0, r=0),
    )
    st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PRODUCT & CATEGORY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Product & Category Analysis")

col_left, col_right = st.columns(2)

with col_left:
    # Revenue by category — horizontal bar so category labels are readable
    cat_rev = (
        fdf.groupby("category")["total_kes"]
        .sum()
        .sort_values()
        .reset_index()
        .rename(columns={"category": "Category", "total_kes": "Revenue (KES)"})
    )
    fig3 = px.bar(
        cat_rev,
        x="Revenue (KES)", y="Category",
        orientation="h",
        title="Revenue by Category",
        color="Revenue (KES)",
        color_continuous_scale="Blues",
    )
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, coloraxis_showscale=False,
        margin=dict(t=40, b=0, l=0, r=0),
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig3, use_container_width=True)

with col_right:
    # Order volume by category — pie chart for share at a glance
    cat_orders = (
        fdf["category"].value_counts()
        .reset_index()
        .rename(columns={"category": "Category", "count": "Orders"})
    )
    fig4 = px.pie(
        cat_orders,
        names="Category", values="Orders",
        title="Order Share by Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        hole=0.45,
    )
    fig4.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    fig4.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig4, use_container_width=True)

# Top 10 products by revenue
st.markdown("#### Top 10 Products by Revenue")
top_products = (
    fdf.groupby("product_name")["total_kes"]
    .sum()
    .nlargest(10)
    .reset_index()
    .rename(columns={"product_name": "Product", "total_kes": "Revenue (KES)"})
    .sort_values("Revenue (KES)")
)
fig5 = px.bar(
    top_products,
    x="Revenue (KES)", y="Product",
    orientation="h",
    color_discrete_sequence=["#818CF8"],
)
fig5.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    margin=dict(t=10, b=0, l=0, r=0),
    yaxis=dict(showgrid=False),
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
)
st.plotly_chart(fig5, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — CUSTOMER DEMOGRAPHICS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Customer Demographics")

col_left, col_right = st.columns(2)

with col_left:
    # Age distribution — histogram with 10-year bins
    fig6 = px.histogram(
        fdf,
        x="age",
        nbins=18,
        title="Customer Age Distribution",
        color_discrete_sequence=["#F59E0B"],
        labels={"age": "Age"},
    )
    fig6.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=0, l=0, r=0),
        bargap=0.05,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Customers"),
    )
    st.plotly_chart(fig6, use_container_width=True)

with col_right:
    # Orders and revenue per city — grouped bar
    city_stats = (
        fdf.groupby("city")
        .agg(orders=("order_id", "count"), revenue=("total_kes", "sum"))
        .sort_values("orders", ascending=False)
        .head(9)
        .reset_index()
    )
    fig7 = px.bar(
        city_stats,
        x="city", y="orders",
        title="Orders by City (Top 9)",
        color="revenue",
        color_continuous_scale="Teal",
        labels={"city": "City", "orders": "Orders", "revenue": "Revenue (KES)"},
    )
    fig7.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=False, tickangle=30),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        coloraxis_colorbar=dict(title="Revenue"),
    )
    st.plotly_chart(fig7, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ORDER FULFILMENT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Order Fulfilment")

col_left, col_mid, col_right = st.columns(3)

with col_left:
    # Order status breakdown
    status_counts = (
        fdf["order_status"].value_counts()
        .reset_index()
        .rename(columns={"order_status": "Status", "count": "Orders"})
    )
    status_colors = {
        "delivered": "#34D399", "shipped": "#60A5FA",
        "pending": "#FBBF24",   "in transit": "#A78BFA",
        "cancelled": "#F87171", "returned": "#FB923C",
    }
    fig8 = px.bar(
        status_counts,
        x="Status", y="Orders",
        title="Orders by Status",
        color="Status",
        color_discrete_map=status_colors,
    )
    fig8.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        showlegend=False, margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig8, use_container_width=True)

with col_mid:
    # Shipping time distribution — only for orders that have shipped
    shipped = fdf[fdf["ship_days"].notna() & (fdf["ship_days"] >= 0)]
    fig9 = px.histogram(
        shipped,
        x="ship_days",
        nbins=20,
        title="Shipping Time Distribution (Days)",
        color_discrete_sequence=["#34D399"],
        labels={"ship_days": "Days to Ship"},
    )
    fig9.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=0, l=0, r=0),
        bargap=0.05,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", title="Orders"),
    )
    st.plotly_chart(fig9, use_container_width=True)

with col_right:
    # Average shipping days by category
    avg_ship_cat = (
        fdf[fdf["ship_days"].notna()]
        .groupby("category")["ship_days"]
        .mean()
        .round(1)
        .sort_values()
        .reset_index()
        .rename(columns={"category": "Category", "ship_days": "Avg Days"})
    )
    fig10 = px.bar(
        avg_ship_cat,
        x="Avg Days", y="Category",
        orientation="h",
        title="Avg Ship Days by Category",
        color_discrete_sequence=["#60A5FA"],
    )
    fig10.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig10, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — PAYMENTS & MARKETING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Payments & Marketing")

col_left, col_right = st.columns(2)

with col_left:
    # Revenue split by payment method
    pay_rev = (
        fdf.groupby("payment_method")["total_kes"]
        .sum()
        .reset_index()
        .rename(columns={"payment_method": "Method", "total_kes": "Revenue (KES)"})
    )
    fig11 = px.pie(
        pay_rev,
        names="Method", values="Revenue (KES)",
        title="Revenue by Payment Method",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig11.update_layout(margin=dict(t=40, b=0, l=0, r=0))
    fig11.update_traces(textposition="outside", textinfo="percent+label")
    st.plotly_chart(fig11, use_container_width=True)

with col_right:
    # Orders by marketing source — exclude "Unknown" for clarity
    mkt = (
        fdf[fdf["marketing_source"] != "Unknown"]["marketing_source"]
        .value_counts()
        .reset_index()
        .rename(columns={"marketing_source": "Source", "count": "Orders"})
    )
    fig12 = px.bar(
        mkt,
        x="Source", y="Orders",
        title="Orders by Marketing Source (excl. Unknown)",
        color="Orders",
        color_continuous_scale="Purples",
    )
    fig12.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig12, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — REVIEW RATINGS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Review Ratings")

col_left, col_right = st.columns(2)

with col_left:
    # Rating distribution — count of each score 1–5
    ratings = (
        fdf["review_rating"].dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
        .rename(columns={"review_rating": "Rating", "count": "Count"})
    )
    fig13 = px.bar(
        ratings,
        x="Rating", y="Count",
        title="Review Rating Distribution",
        color="Rating",
        color_continuous_scale="RdYlGn",
    )
    fig13.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=False, dtick=1),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig13, use_container_width=True)

with col_right:
    # Average rating per category
    avg_rating_cat = (
        fdf.groupby("category")["review_rating"]
        .mean()
        .round(2)
        .sort_values()
        .reset_index()
        .rename(columns={"category": "Category", "review_rating": "Avg Rating"})
    )
    fig14 = px.bar(
        avg_rating_cat,
        x="Avg Rating", y="Category",
        orientation="h",
        title="Average Rating by Category",
        color="Avg Rating",
        color_continuous_scale="RdYlGn",
        range_color=[1, 5],
    )
    fig14.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0", range=[0, 5]),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig14, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — RAW DATA EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## Raw Data Explorer")

# st.expander hides content behind a toggle so it doesn't clutter the page
with st.expander("Click to view filtered data table"):
    st.dataframe(
        fdf[[
            "order_id", "customer_name", "city", "category",
            "product_name", "qty", "total_kes", "order_status",
            "payment_method", "order_date", "review_rating"
        ]].reset_index(drop=True),
        use_container_width=True,
        height=400,
    )
    # Download button lets users export the current filtered view as CSV
    csv = fdf.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv,
        file_name="filtered_orders.csv",
        mime="text/csv",
    )

st.caption("Dashboard built with Streamlit & Plotly · East Africa E-Commerce Dataset")
