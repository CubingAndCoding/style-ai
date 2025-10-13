# Style AI Backend Deployment Guide

## Quick Start - Railway (Recommended)

### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Prepare for production deployment"
git push origin main
```

### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your Style AI repository
5. Railway will auto-detect it's a Python/Flask app

### 3. Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

**Required Variables:**
```
JWT_SECRET_KEY=your-super-secure-random-key-here
GOOGLE_API_KEY=your-gemini-api-key
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

**Optional Variables:**
```
FLASK_ENV=production
LOG_LEVEL=INFO
```

### 4. Add Database
1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Railway will automatically connect it to your app
3. Update your app to use the `DATABASE_URL` environment variable

### 5. Deploy
Railway will automatically build and deploy your app. You'll get a URL like:
`https://your-app-name.railway.app`

---

## Alternative: Render Deployment

### 1. Prepare Repository
Same as Railway - commit all changes

### 2. Deploy to Render
1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app`
   - **Python Version**: 3.11

### 3. Configure Environment Variables
Same variables as Railway above

### 4. Add Database
1. Create a PostgreSQL database in Render
2. Copy the connection string to `DATABASE_URL` environment variable

---

## Production Checklist

### Security
- [ ] Change `JWT_SECRET_KEY` to a strong random string
- [ ] Use production Stripe keys (`sk_live_...`)
- [ ] Set `FLASK_ENV=production`
- [ ] Configure CORS for your frontend domain only

### Database
- [ ] Switch from SQLite to PostgreSQL
- [ ] Set up database backups
- [ ] Configure connection pooling

### Monitoring
- [ ] Set up error tracking (Sentry recommended)
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring

### Performance
- [ ] Configure CDN for static files
- [ ] Set up Redis for caching (optional)
- [ ] Configure auto-scaling

### Domain & SSL
- [ ] Set up custom domain
- [ ] Configure SSL certificate (automatic on Railway/Render)
- [ ] Update frontend API URLs

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET_KEY` | ✅ | Secret key for JWT tokens |
| `GOOGLE_API_KEY` | ✅ | Google Gemini API key |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook secret |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `FLASK_ENV` | ✅ | Set to `production` |
| `LOG_LEVEL` | ❌ | Logging level (INFO/DEBUG) |
| `CORS_ORIGINS` | ❌ | Allowed frontend domains |

---

## Troubleshooting

### Common Issues

**Build Fails:**
- Check Python version (3.11 recommended)
- Verify all dependencies in requirements.txt
- Check for missing system packages

**App Won't Start:**
- Verify environment variables are set
- Check database connection
- Review logs for specific errors

**Database Errors:**
- Ensure PostgreSQL is running
- Check connection string format
- Verify database permissions

**API Errors:**
- Check API keys are valid
- Verify CORS configuration
- Test endpoints individually

### Getting Help
- Check platform-specific documentation (Railway/Render)
- Review Flask deployment guides
- Test locally with production settings first

---

## Cost Estimates

| Platform | Monthly Cost | Features |
|----------|--------------|----------|
| Railway | $5-20 | Auto-scaling, database included |
| Render | $7-25 | Free tier available |
| DigitalOcean | $12-25 | Predictable pricing |
| AWS/GCP | $20-100+ | Enterprise features |

*Prices may vary based on usage and region*


