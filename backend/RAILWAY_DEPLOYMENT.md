# Railway Deployment Checklist

## Quick Deploy Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Update backend for Railway deployment"
   git push origin main
   ```

2. **Railway will automatically deploy** when you push to your connected branch

## Pre-Deployment Checklist

### Environment Variables (Set in Railway Dashboard → Variables)

Required variables from `production.env.template`:

- `FLASK_ENV=production`
- `FLASK_APP=app.py`
- `JWT_SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `GOOGLE_API_KEY` (your Gemini API key)
- `STRIPE_SECRET_KEY` (production Stripe key)
- `STRIPE_WEBHOOK_SECRET` (if using webhooks)
- `CORS_ORIGINS` (your frontend domain or `*` for development)

Optional but recommended:
- `LOG_LEVEL=INFO`
- `RATE_LIMIT_PER_MINUTE=60`
- `RATE_LIMIT_PER_HOUR=1000`

### Database Setup

- Railway will automatically provide `DATABASE_URL` if you add PostgreSQL service
- The app will use `DATABASE_URL` automatically (no need to set `SQLALCHEMY_DATABASE_URI`)

### File Configuration

- `railway.json` - Configured to use Dockerfile and PORT from environment
- `Dockerfile` - Set up to use Railway's PORT environment variable
- Health check endpoint: `/health` (Railway can use this for monitoring)

## Verify Deployment

After deployment, check:

1. **Health endpoint**: `https://your-app.railway.app/health`
2. **API status**: `https://your-app.railway.app/rate-limit-status`
3. **Logs**: Check Railway dashboard logs for any errors

## Troubleshooting

- **Port issues**: Railway sets `PORT` automatically - don't hardcode it
- **Database connection**: Ensure PostgreSQL service is added and `DATABASE_URL` is set
- **API keys**: Verify all required API keys are set in Railway Variables
- **Build failures**: Check Railway build logs for dependency issues

## Notes

- The `railway.json` file configures Railway to use the Dockerfile
- Gunicorn is configured with 4 workers and 120s timeout
- All logs go to stdout/stderr (Railway captures these automatically)
- Uploads directory is created at `/app/uploads` in the container

