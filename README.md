# 🛒 E-Commerce Sales Dashboard

An interactive dashboard built with **Streamlit** and **Plotly** on top of a cleaned East Africa e-commerce orders dataset (4,831 orders · 2023–2025).

## Live Demo

> Deploy to Streamlit Community Cloud and paste your URL here.

## Dashboard Sections

| Section | What it shows |
|---|---|
| **KPI Cards** | Total orders, revenue, avg order value, avg rating, avg ship days, top city |
| **Sales Trends** | Monthly revenue (area chart) and order volume (bar chart) |
| **Product & Category** | Revenue by category, order share pie, top 10 products |
| **Customer Demographics** | Age distribution histogram, orders by city |
| **Order Fulfilment** | Status breakdown, shipping time distribution, avg ship days by category |
| **Payments & Marketing** | Revenue by payment method, orders by marketing source |
| **Review Ratings** | Rating distribution, avg rating per category |
| **Data Explorer** | Filterable table with CSV download |

All charts respond to the sidebar filters (date range, city, category, order status).

## Project Structure

```
ecommerce-dashboard/
├── app.py                     # Main Streamlit application
├── orders_clean.csv           # Cleaned dataset (output from data cleaning project)
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml            # Theme and server settings
└── .gitignore
```

## How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ecommerce-dashboard.git
cd ecommerce-dashboard

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Opens at `http://localhost:8501` in your browser.

## Deploy to Streamlit Community Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → connect your GitHub account
4. Select this repo, set **Main file** to `app.py`
5. Click **Deploy**

Your app gets a public URL like `yourname-ecommerce-dashboard.streamlit.app`.
It rebuilds automatically on every `git push`.

## Data Source

This dashboard uses `orders_clean.csv` — the output of the companion
[data cleaning project](https://github.com/YOUR_USERNAME/ecommerce-data-cleaning).

## Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Core language |
| Streamlit | ≥ 1.35 | Dashboard framework |
| Plotly | ≥ 5.0 | Interactive charts |
| pandas | ≥ 2.0 | Data manipulation |

## Author

**Your Name** · [GitHub](https://github.com/yourusername) · [LinkedIn](https://linkedin.com/in/yourprofile)

## License

[MIT License](https://opensource.org/licenses/MIT)
