# Job Tracker — Setup Guide

---

## Step 1 — Supabase (free database)

1. Go to **supabase.com** → Sign up → New Project
2. Give it a name (e.g. `job-tracker`), set a database password, pick a region (US East)
3. Wait ~2 min for it to finish provisioning
4. Go to the **SQL Editor** (left sidebar) and run this to create the jobs table:

```sql
create table jobs (
  id bigint generated always as identity primary key,
  title text not null,
  url text,
  salary text,
  notes text,
  status text default 'not applied',
  date_added date default current_date
);
```

5. Go to **Project Settings → API** (left sidebar)
6. Copy two values — you'll need them shortly:
   - **Project URL** → this is your `SUPABASE_URL`
   - **anon / public** key → this is your `SUPABASE_ANON_KEY`

---

## Step 2 — Push to GitHub

In your terminal inside the project folder:

```
git add .
git commit -m "job tracker"
```

If you haven't linked a GitHub repo yet:
```
git remote add origin https://github.com/YOUR_USERNAME/job-tracker.git
git push -u origin main
```

Otherwise just:
```
git push
```

---

## Step 3 — Deploy on Render (free hosting)

1. Go to **render.com** → Sign up with GitHub
2. Click **New → Web Service**
3. Connect your `job-tracker` GitHub repo
4. Fill in:
   - **Build Command:** `npm install`
   - **Start Command:** `npm start`
   - **Instance Type:** Free
5. Click **Environment** and add these 3 variables:

| Key | Value |
|-----|-------|
| `SUPABASE_URL` | (paste from Supabase) |
| `SUPABASE_ANON_KEY` | (paste from Supabase) |
| `APP_PASSWORD` | (pick any password to give her) |

6. Click **Create Web Service** — Render builds and deploys it (~2 min)
7. You'll get a URL like `https://job-tracker-xxxx.onrender.com` — share that + the password with her

**Note:** The free tier sleeps after 15 min of inactivity. First visit after sleeping takes ~30 sec to load — totally normal. Her job data lives in Supabase so nothing gets lost.

---

## Local development

```
npm install
```

Create a `.env` file (copy from `.env.example`) and fill in your Supabase credentials + a password.

```
npm start
```

Open http://localhost:3000

---

## How to use

- Click any job board button → opens a pre-filtered search in a new tab
- Find a job she likes → paste the URL + title into the Add form
- Update the status dropdown as she applies: **Not Applied → Applied → Heard Back → Offer → Rejected**
- Use the Notes field for interview times, contact names, anything useful
- Filter pills at the top let her focus on one status group at a time
