# Frontend Deployment to Render (Free Tier)

## Quick Deploy Steps

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (free)
3. Connect your GitHub account

### Step 2: Create New Static Site or Web Service

**Option A: Static Site (Recommended for Frontend)**
1. Click **"New +"** → **"Static Site"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `style-ai-frontend`
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `frontend/style-ai`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
   - **Environment**: `Node`
   - **Node Version**: `18` (or latest LTS)

**Option B: Web Service (If you need server-side features)**
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `style-ai-frontend`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: `frontend/style-ai`
   - **Runtime**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npx serve -s dist -l $PORT`
   - **Plan**: **Free**

### Step 3: Set Environment Variables

In your service → **Environment** tab, add:

```
NODE_ENV=production
VITE_API_URL=https://style-ai-backend.onrender.com
VITE_APP_NAME=Style AI
VITE_APP_VERSION=0.0.1
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key_here
VITE_DEBUG_MODE=false
VITE_ENABLE_CONSOLE_LOGS=false
```

**Important:** 
- Replace `VITE_STRIPE_PUBLISHABLE_KEY` with your actual Stripe publishable key
- These variables are used at **build time** (Vite embeds them in the static files)

### Step 4: Deploy

1. Click **"Create Static Site"** or **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies (`npm install`)
   - Build the app (`npm run build`)
   - Serve the built files from `dist/` folder

### Step 5: Verify Deployment

1. Your app will be available at: `https://style-ai-frontend.onrender.com` (or your custom name)
2. Test that it connects to your backend
3. Check browser console for any errors

## Using render.yaml (Alternative)

If you prefer automatic configuration:

1. The `render.yaml` file is already configured
2. In Render dashboard, go to **"New +"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render will automatically detect `render.yaml` and configure everything

## Environment Variables Explained

- **VITE_API_URL**: Your backend API URL (already set to Render backend)
- **VITE_STRIPE_PUBLISHABLE_KEY**: Your Stripe publishable key (starts with `pk_live_` for production)
- **VITE_APP_NAME**: App name (optional)
- **VITE_APP_VERSION**: App version (optional)
- **NODE_ENV**: Set to `production` for optimized builds

## Free Tier Limitations

- **Spins down after 15 minutes of inactivity** (first request after spin-down takes ~30 seconds)
- **750 hours/month** of runtime
- **512 MB RAM**
- **Limited CPU** (builds may take longer)

## Troubleshooting

### Build Fails:
- Check that `package.json` has all required dependencies
- Verify Node version is compatible (18+)
- Check build logs for specific errors

### App doesn't connect to backend:
- Verify `VITE_API_URL` is set correctly in environment variables
- Check browser console for CORS errors
- Ensure backend CORS settings allow your frontend domain

### Static assets not loading:
- Verify `dist/` folder is being served correctly
- Check that `vite.config.ts` has correct `outDir: 'dist'`
- Ensure `Publish Directory` is set to `dist` in Render settings

## Custom Domain (Optional)

1. Go to your service → **Settings** → **Custom Domains**
2. Add your domain
3. Follow DNS configuration instructions
4. SSL certificate is automatically provisioned

## Next Steps

After deployment:
- Test all features (login, upload, payment, etc.)
- Monitor performance and errors
- Consider upgrading to **Starter** plan ($7/month) for always-on service
- Set up monitoring and alerts

