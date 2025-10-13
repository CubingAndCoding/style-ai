# Frontend Deployment Guide

This guide will help you deploy your Style AI frontend to Railway, maintaining consistency with your backend deployment.

## Prerequisites

1. Railway account (you already have this for your backend)
2. Your backend deployed and running on Railway
3. Stripe account with publishable key

## Deployment Steps

### 1. Prepare Environment Variables

1. Copy the environment template:
   ```bash
   cp env.production.template .env.production
   ```

2. Edit `.env.production` with your actual values:
   - Replace `https://your-backend-app.railway.app` with your actual Railway backend URL
   - Replace `pk_live_your_stripe_publishable_key_here` with your actual Stripe publishable key

### 2. Deploy to Railway

#### Option A: Using Railway CLI (Recommended)

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Navigate to your frontend directory:
   ```bash
   cd frontend/style-ai
   ```

4. Initialize Railway project:
   ```bash
   railway init
   ```

5. Set environment variables:
   ```bash
   railway variables set VITE_API_URL=https://your-backend-app.railway.app
   railway variables set VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
   railway variables set VITE_APP_NAME="Style AI"
   railway variables set VITE_DEBUG_MODE=false
   railway variables set VITE_ENABLE_CONSOLE_LOGS=false
   ```

6. Deploy:
   ```bash
   railway up
   ```

#### Option B: Using Railway Dashboard

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Select the `frontend/style-ai` directory as the root
6. Railway will automatically detect the Dockerfile and deploy

### 3. Configure Environment Variables in Railway Dashboard

1. Go to your project dashboard
2. Click on your frontend service
3. Go to "Variables" tab
4. Add the following environment variables:
   - `VITE_API_URL`: Your backend Railway URL
   - `VITE_STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
   - `VITE_APP_NAME`: "Style AI"
   - `VITE_DEBUG_MODE`: "false"
   - `VITE_ENABLE_CONSOLE_LOGS`: "false"

### 4. Custom Domain (Optional)

1. In Railway dashboard, go to your frontend service
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow Railway's DNS configuration instructions

## Alternative Deployment Options

### Vercel (Recommended Alternative)

If you prefer Vercel for frontend deployment:

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to frontend directory:
   ```bash
   cd frontend/style-ai
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Set environment variables in Vercel dashboard

### Netlify

1. Connect your GitHub repository to Netlify
2. Set build command: `npm run build`
3. Set publish directory: `dist`
4. Configure environment variables in Netlify dashboard

## Troubleshooting

### Common Issues

1. **Build Failures**: Check that all dependencies are in `package.json`
2. **Environment Variables**: Ensure all `VITE_` prefixed variables are set
3. **API Connection**: Verify your backend URL is correct and accessible
4. **Stripe Issues**: Ensure you're using the correct publishable key for your environment

### Debugging

1. Check Railway logs in the dashboard
2. Enable console logs temporarily by setting `VITE_ENABLE_CONSOLE_LOGS=true`
3. Test API connectivity from your frontend

## Production Checklist

- [ ] Environment variables configured
- [ ] Backend API URL updated
- [ ] Stripe publishable key set
- [ ] Debug mode disabled
- [ ] Custom domain configured (if needed)
- [ ] SSL certificate active
- [ ] Performance monitoring set up

## Monitoring

Railway provides built-in monitoring for:
- Application logs
- Performance metrics
- Error tracking
- Resource usage

Access these in your Railway dashboard under the "Metrics" tab.

## Updates and Maintenance

To update your frontend:

1. Make changes to your code
2. Commit and push to your repository
3. Railway will automatically redeploy (if auto-deploy is enabled)
4. Or manually trigger deployment: `railway up`

## Support

- Railway Documentation: https://docs.railway.app/
- Vite Documentation: https://vitejs.dev/guide/
- Ionic Documentation: https://ionicframework.com/docs

