# Who Made It - Deployment Guide

## Overview
This guide will help you deploy the "Who Made It" app independently from Emergent, using:
- **Frontend**: Vercel (already deployed)
- **Backend**: Render.com (free tier)
- **Database**: MongoDB Atlas (free tier)

## Prerequisites
✅ GitHub account (connected)
✅ Render.com account (connected to GitHub)
✅ MongoDB Atlas account
✅ OpenAI API key with billing enabled

---

## Step 1: Set Up MongoDB Atlas

1. Go to https://cloud.mongodb.com/
2. Sign in with your GitHub account
3. Click **"Build a Database"**
4. Select **"M0 FREE"** tier
5. Choose a cloud provider and region (closest to your users)
6. Cluster Name: `who-made-it-cluster`
7. Click **"Create Cluster"** (takes 1-3 minutes)

### Get Connection String:
1. Click **"Connect"** on your cluster
2. Select **"Connect your application"**
3. Copy the connection string (looks like):
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your actual database password
5. Save this connection string - you'll need it for Render

### Create Database User:
1. Go to **"Database Access"** in left sidebar
2. Click **"Add New Database User"**
3. Username: `whomadeit`
4. Password: Generate a secure password (save it!)
5. Database User Privileges: **"Read and write to any database"**
6. Click **"Add User"**

### Allow Network Access:
1. Go to **"Network Access"** in left sidebar
2. Click **"Add IP Address"**
3. Click **"Allow Access From Anywhere"** (0.0.0.0/0)
4. Click **"Confirm"**

---

## Step 2: Add Billing to OpenAI Account

Your API key needs billing enabled:

1. Go to https://platform.openai.com/account/billing
2. Click **"Add payment method"**
3. Add your credit card
4. Set a usage limit (recommended: $10/month to start)
5. Verify your key works: https://platform.openai.com/api-keys

---

## Step 3: Deploy Backend to Render.com

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect account"** if not connected to GitHub
4. Find and select **"Who-Made-It"** repository
5. Configure the service:

   **Basic Settings:**
   - Name: `who-made-it-backend`
   - Region: Choose closest to you
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements-production.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

   **Instance Type:**
   - Select **"Free"** tier

   **Environment Variables (click "Add Environment Variable"):**
   ```
   OPENAI_API_KEY = your_openai_api_key_here
   MONGO_URL = your_mongodb_connection_string_here
   DB_NAME = who_made_it
   CORS_ORIGINS = *
   ```

6. Click **"Create Web Service"**
7. Wait for deployment (5-10 minutes)
8. Once deployed, copy your backend URL (looks like):
   ```
   https://who-made-it-backend.onrender.com
   ```

---

## Step 4: Update Frontend Environment Variable on Vercel

1. Go to https://vercel.com/dashboard
2. Select your **"Who Made It"** project
3. Go to **"Settings"** → **"Environment Variables"**
4. Find `REACT_APP_BACKEND_URL`
5. Update its value to your Render backend URL:
   ```
   https://who-made-it-backend.onrender.com
   ```
6. Click **"Save"**
7. Go to **"Deployments"** tab
8. Click **"..."** on latest deployment → **"Redeploy"**
9. Click **"Redeploy"** to confirm

---

## Step 5: Test Your Deployed App

1. Visit your Vercel app URL
2. Try searching for an invention (e.g., "Light Bulb")
3. Verify:
   - ✅ Results appear
   - ✅ Scoreboard updates
   - ✅ Categories display
   - ✅ Milestone counter works

---

## Troubleshooting

### Backend not responding:
1. Check Render logs: Dashboard → your-service → "Logs" tab
2. Verify environment variables are set correctly
3. Ensure MongoDB connection string is correct (password included)

### OpenAI errors:
1. Verify API key has billing enabled
2. Check usage limits: https://platform.openai.com/account/usage
3. Ensure key hasn't expired

### Database connection errors:
1. Verify MongoDB Atlas is allowing connections from anywhere (0.0.0.0/0)
2. Check connection string format (should start with `mongodb+srv://`)
3. Ensure password in connection string doesn't have special characters (if it does, URL-encode them)

### Free Tier Limitations:

**Render.com Free Tier:**
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds (cold start)
- 750 hours/month free

**MongoDB Atlas Free Tier:**
- 512 MB storage
- Shared RAM
- No backups (paid feature)

**To avoid cold starts on Render:**
- Upgrade to paid tier ($7/month)
- Or use a service like UptimeRobot to ping your backend every 10 minutes

---

## Cost Estimation

- **Vercel**: Free (Frontend)
- **Render**: Free with cold starts, $7/month for always-on
- **MongoDB Atlas**: Free (M0 tier)
- **OpenAI API**: ~$0.50-$2 per 1000 queries (gpt-4o-mini)

**Total Monthly Cost**: $0-$10 depending on usage and whether you want 24/7 uptime

---

## Your App is Now Independent! 🎉

Your app now runs completely independently from Emergent:
- ✅ Backend hosted on Render.com
- ✅ Frontend hosted on Vercel
- ✅ Database hosted on MongoDB Atlas
- ✅ Uses your own OpenAI API key

Even if Emergent is inactive, your app will continue to work!
