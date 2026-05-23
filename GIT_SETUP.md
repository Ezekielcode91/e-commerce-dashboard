# Git & GitHub Setup

## Step 1 — Open the folder in VS Code

File → Open Folder → select `ecommerce-dashboard`.

## Step 2 — Open the terminal

Press `Ctrl + `` ` `` ` to open the integrated terminal.

## Step 3 — Initialise a local Git repo

```bash
git init
git add .
git commit -m "Initial commit: Streamlit dashboard"
```

## Step 4 — Create a repo on GitHub

1. Go to https://github.com/new
2. Name: `ecommerce-dashboard`
3. Set to **Public**
4. Do NOT tick "Add README" or "Add .gitignore" — you already have them
5. Click **Create repository**

## Step 5 — Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ecommerce-dashboard.git
git branch -M main
git push -u origin main
```

## Step 6 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io
2. Click **New app**
3. Connect your GitHub account if prompted
4. Select the `ecommerce-dashboard` repo
5. Set **Main file path** to `app.py`
6. Click **Deploy**

Done — your dashboard is live at a public URL.

## Future updates

```bash
git add .
git commit -m "Describe your change"
git push
```

Streamlit Cloud rebuilds automatically on every push.
