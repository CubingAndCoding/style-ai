# Complete Stripe Setup Guide

## ✅ What's Already Done

Your Stripe integration is fully implemented with:

### Backend Endpoints:
- `POST /auth/create-payment-intent` - Creates Stripe payment intents
- `POST /auth/confirm-payment` - Confirms payments and adds credits
- `POST /auth/purchase-credits` - Legacy endpoint (simulated payment)

### Frontend Components:
- Stripe Elements for secure card input
- Payment form with proper validation
- Success/error handling
- Credit addition after successful payment

## 🚀 Testing Your Setup

### 1. Start Your Servers

**Backend:**
```bash
cd "X:\Projects\Personal Projects\Style AI\backend"
python app.py
```

**Frontend:**
```bash
cd "X:\Projects\Personal Projects\Style AI\frontend\style-ai"
npm run dev
```

### 2. Test the Payment Flow

1. **Open your app** in browser (usually `http://localhost:8100`)
2. **Register/Login** to your account
3. **Navigate to payment page** (`/stripe-payment`)
4. **Use test card**: `4242 4242 4242 4242`
   - **Expiry**: Any future date (e.g., `12/25`)
   - **CVC**: Any 3 digits (e.g., `123`)

### 3. Expected Results

✅ **Successful Payment Flow:**
1. Card input appears and accepts typing
2. Payment processes without errors
3. Success message shows
4. 25 credits added to your account
5. Redirects to camera page

## 🔧 Troubleshooting

### If Backend Won't Start:
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Install missing dependencies
pip install -r requirements.txt
```

### If Frontend Won't Start:
```bash
# Clear cache and reinstall
npm cache clean --force
npm install
npm run dev
```

### If Payment Fails:
1. **Check browser console** for JavaScript errors
2. **Check backend terminal** for error messages
3. **Verify Stripe keys** are correct in `.env` files
4. **Test with debug page**: `http://localhost:8100/stripe-debug`

## 📋 Environment Files Checklist

### Frontend (`frontend/style-ai/.env`):
```env
VITE_API_URL=http://localhost:5000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_key_here
```

### Backend (`backend/.env`):
```env
STRIPE_SECRET_KEY=sk_test_your_actual_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

## 🎯 Test URLs

- **Main Payment**: `http://localhost:8100/stripe-payment`
- **Debug Page**: `http://localhost:8100/stripe-debug`
- **Fixed Version**: `http://localhost:8100/stripe-payment-fixed`

## 💳 Test Card Numbers

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Insufficient Funds**: `4000 0000 0000 9995`

Use any future expiry date and any 3-digit CVC.

## 🚀 Going Live (Production)

When ready for production:

1. **Switch to Live Mode** in Stripe Dashboard
2. **Get Live Keys** (replace test keys)
3. **Update Environment Variables**
4. **Test with Real Cards** (small amounts first)
5. **Set up Webhooks** (optional but recommended)

## 📞 Support

If you encounter issues:
1. Check the debug page first
2. Look at browser console errors
3. Check backend terminal output
4. Verify all environment variables are set

Your Stripe integration is ready to use! 🎉


