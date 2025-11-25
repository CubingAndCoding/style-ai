# Render Free Tier Deployment Guide

## Quick Deploy to Render (Free Tier)

Render offers a free tier perfect for testing your backend. Here's how to deploy:

## Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (free)
3. Connect your GitHub account

## Step 2: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select the repository containing your backend
4. Configure the service:
   - **Name**: `style-ai-backend` (or your preferred name)
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app`
   - **Plan**: **Free** (for testing)

## Step 3: Add PostgreSQL Database (Free)

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `style-ai-db`
   - **Database**: `style_ai`
   - **User**: (auto-generated)
   - **Region**: Same as your web service
   - **Plan**: **Free**
3. Copy the **Internal Database URL** (starts with `postgresql://`)

## Step 4: Set Environment Variables

In your web service → **Environment** tab, add these variables:

### Required Variables:
```
FLASK_ENV=production
FLASK_APP=app.py
GOOGLE_API_KEY=your-google-gemini-api-key
JWT_SECRET_KEY=your-generated-jwt-secret-key
DATABASE_URL=<paste the Internal Database URL from PostgreSQL service>
```

### Optional but Recommended:
```
LOG_LEVEL=INFO
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Generate JWT Secret Key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Start your app
3. Watch the build logs for any errors

## Step 6: Initialize Database

After first deployment, you may need to initialize the database schema:

1. Go to your web service → **Shell** tab
2. Run:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

Or if you have migration scripts, run them in the Shell.

## Step 7: Verify Deployment

1. Your app will be available at: `https://style-ai-backend.onrender.com` (or your custom name)
2. Test health endpoint: `https://your-app.onrender.com/health`
3. Test API: `https://your-app.onrender.com/rate-limit-status`

## Free Tier Limitations

- **Spins down after 15 minutes of inactivity** (first request after spin-down takes ~30 seconds)
- **750 hours/month** of runtime (enough for testing)
- **512 MB RAM**
- **Limited CPU** (may be slower than paid tiers)

## Troubleshooting

### App won't start:
- Check build logs for dependency errors
- Verify all environment variables are set
- Check that `PORT` is used (Render sets this automatically)

### Database connection issues:
- Ensure `DATABASE_URL` is set correctly
- Use **Internal Database URL** (not external) for better performance
- Check PostgreSQL service is running

### Timeout errors:
- Free tier has slower cold starts
- First request after spin-down may timeout - just retry

## Alternative: Use render.yaml

If you prefer, you can use the `render.yaml` file:

1. In Render dashboard, go to **"New +"** → **"Blueprint"**
2. Connect your GitHub repo
3. Render will automatically detect `render.yaml` and configure everything

## Next Steps

Once deployed and tested:
- Upgrade to **Starter** plan ($7/month) for always-on service
- Add custom domain
- Set up monitoring and alerts

