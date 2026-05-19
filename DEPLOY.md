# Deploy cliffIT Solutions to Render

## Step 1: Create a GitHub Repository

Open Terminal and run these commands:

```bash
cd ~/projects/cliffIT-solutions
git init
git add -A
git commit -m "Initial commit: cliffIT Solutions website"
```

Then go to https://github.com/new, create a new repo called `cliffIT-solutions` (keep it public or private), and run:

```bash
git remote add origin https://github.com/YOUR_USERNAME/cliffIT-solutions.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

1. Go to https://render.com and sign up (free tier works)
2. Click **New → Web Service**
3. Connect your GitHub account and select the `cliffIT-solutions` repo
4. Render will auto-detect `render.yaml` — settings will be pre-filled:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Environment:** Python
5. Click **Deploy**

Your site will be live at `https://cliffit-solutions.onrender.com` within a few minutes.

## Notes

- Free tier apps sleep after 15 minutes of inactivity (first visit after sleep takes ~30 seconds)
- The SQLite database resets on each deploy — for persistent data, consider upgrading to Render's PostgreSQL
