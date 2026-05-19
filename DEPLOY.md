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
- Admin edits are stored in SQLite. On Render, `render.yaml` mounts a persistent disk at `/var/data` and sets `DATABASE_PATH=/var/data/cliffIT.db` so website updates survive restarts and deploys.
- Persistent disks require a paid Render web service. If you stay on the free tier, use Render Postgres or another external database for saved admin updates.
- Contact form email notifications use SMTP when these Render environment variables are set: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, and optionally `SMTP_FROM_EMAIL` and `SMTP_USE_TLS`. Notifications are sent to the Site Settings contact form email, defaulting to `hr@cliffitsolutions.com`.
