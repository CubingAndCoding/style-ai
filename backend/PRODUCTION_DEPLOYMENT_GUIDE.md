# 🚀 Production Deployment Guide - Style AI Backend

This guide will walk you through deploying your Flask backend to production on Railway.

## 📋 Prerequisites

- [Railway account](https://railway.app) (free tier available)
- [GitHub repository](https://github.com) with your code
- API keys for AI services (Google Gemini, Hugging Face, etc.)
- Stripe account for payments

## 🔧 Step 1: Prepare Your Environment Variables

### Generate Secure Keys

```bash
# Generate JWT secret key
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate Flask secret key
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Required Environment Variables

Copy these variables to your Railway project's Variables tab:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_APP=app.py

# Security (CRITICAL - Use generated keys above)
JWT_SECRET_KEY=your-generated-jwt-secret-key
SECRET_KEY=your-generated-flask-secret-key

# Database (Railway will set DATABASE_URL if you add PostgreSQL)
SQLALCHEMY_DATABASE_URI=sqlite:///style_ai.db

# AI Service Keys (At least one required)
GOOGLE_API_KEY=your-google-gemini-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
OPENAI_API_KEY=your-openai-api-key

# Stripe Configuration (Production Keys)
STRIPE_SECRET_KEY=sk_live_your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=whsec_your-stripe-webhook-secret

# File Storage
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216

# Logging
LOG_LEVEL=INFO

# CORS (Update with your frontend domain)
CORS_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Production Settings
DEBUG=False
TESTING=False
```

## 🚂 Step 2: Deploy to Railway

### Option A: Deploy from GitHub

1. **Connect GitHub Repository**
   - Go to [Railway Dashboard](https://railway.app/dashboard)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Service**
   - Railway will detect your `Dockerfile`
   - Set the root directory to `backend/`
   - Railway will automatically build and deploy

### Option B: Deploy with Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

## 🗄️ Step 3: Database Setup

### Option A: PostgreSQL (Recommended for Production)

1. **Add PostgreSQL Service**
   - In Railway dashboard, click "New Service"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

2. **Update Environment Variables**
   - Remove `SQLALCHEMY_DATABASE_URI` (Railway will use `DATABASE_URL`)
   - Your app will automatically use PostgreSQL

### Option B: SQLite (Simple Setup)

- Keep `SQLALCHEMY_DATABASE_URI=sqlite:///style_ai.db`
- Files will be stored in Railway's ephemeral storage
- **Note**: Data will be lost on service restart

## 🔐 Step 4: Security Configuration

### Generate Production Keys

```bash
# Generate secure keys
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Update CORS Origins

Replace `CORS_ORIGINS` with your actual frontend domains:

```bash
# For single domain
CORS_ORIGINS=https://your-app.com

# For multiple domains
CORS_ORIGINS=https://your-app.com,https://www.your-app.com,https://app.your-app.com
```

## 🔑 Step 5: API Keys Setup

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create new API key
3. Set `GOOGLE_API_KEY` in Railway

### Hugging Face API
1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create new token
3. Set `HUGGINGFACE_API_KEY` in Railway

### Stripe Configuration
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Get your **Live** secret key (`sk_live_...`)
3. Set up webhook endpoint
4. Set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in Railway

## 📊 Step 6: Monitoring & Logs

### View Logs
- Go to Railway dashboard
- Click on your service
- View "Logs" tab for real-time logs

### Health Check
Your app includes a health check endpoint:
- `GET /health` - Returns service status

### Rate Limiting Status
- `GET /rate-limit-status` - View current rate limiting status

## 🔧 Step 7: Production Optimizations

### Environment-Specific Settings

Your app automatically detects production environment:

```python
# Production optimizations enabled when FLASK_ENV=production
- Reduced logging verbosity
- Optimized CORS settings
- Production-grade error handling
- Security headers
```

### Performance Tuning

```bash
# Adjust worker count based on your needs
# In railway.json or Dockerfile CMD:
gunicorn --workers 4 --timeout 120 app:app
```

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check if DATABASE_URL is set
   railway variables
   ```

2. **CORS Errors**
   ```bash
   # Ensure CORS_ORIGINS includes your frontend domain
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

3. **API Key Errors**
   ```bash
   # Check logs for missing API keys
   railway logs
   ```

4. **File Upload Issues**
   ```bash
   # Ensure UPLOAD_FOLDER is writable
   UPLOAD_FOLDER=/app/uploads
   ```

### Debug Mode (Temporary)

For debugging, temporarily enable debug mode:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

**⚠️ Remember to disable debug mode in production!**

## 📈 Step 8: Scaling & Performance

### Railway Scaling
- Railway automatically scales based on traffic
- Upgrade to paid plan for better performance
- Monitor usage in Railway dashboard

### Database Scaling
- PostgreSQL scales automatically on Railway
- Consider read replicas for high traffic

### File Storage
- Railway provides ephemeral storage
- Consider external storage (AWS S3) for production

## 🔄 Step 9: Continuous Deployment

### Automatic Deployments
- Railway automatically deploys on git push
- Set up branch protection rules
- Use staging environment for testing

### Environment Management
```bash
# Production environment
FLASK_ENV=production

# Staging environment  
FLASK_ENV=staging
```

## ✅ Step 10: Final Checklist

- [ ] Environment variables set in Railway
- [ ] Database configured (PostgreSQL recommended)
- [ ] API keys configured
- [ ] Stripe webhook configured
- [ ] CORS origins updated
- [ ] Debug mode disabled
- [ ] Health check working
- [ ] Logs monitoring
- [ ] Domain configured (if using custom domain)

## 🎉 You're Live!

Your Flask backend is now running in production on Railway!

### Next Steps:
1. Test all endpoints
2. Configure custom domain (optional)
3. Set up monitoring alerts
4. Deploy your frontend
5. Test the full application

## 📞 Support

- [Railway Documentation](https://docs.railway.app)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Your App Logs](https://railway.app/dashboard) - Check logs for issues

---

**Happy Deploying! 🚀**
