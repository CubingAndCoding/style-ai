# Stripe Integration Setup Guide

This guide will help you set up Stripe payment integration for your Style AI project.

## 1. Get Your Stripe Keys

### Create Stripe Account
1. Go to [stripe.com](https://stripe.com) and sign up for a free account
2. Complete the account verification process
3. You'll start in **Test Mode** (perfect for development)

### Get API Keys
1. In your Stripe Dashboard, go to **Developers** → **API Keys**
2. You'll see two keys:
   - **Publishable key** (starts with `pk_test_`) - Safe to use in frontend
   - **Secret key** (starts with `sk_test_`) - Keep this secret, backend only

## 2. Set Up Environment Variables

### Frontend Environment (.env file in `frontend/style-ai/`)
Create a `.env` file in the `frontend/style-ai/` directory:

```env
VITE_API_URL=http://localhost:5000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_actual_publishable_key_here
```

### Backend Environment (.env file in `backend/`)
Create a `.env` file in the `backend/` directory:

```env
# AI API Keys (if you have them)
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
REPLICATE_API_KEY=your_replicate_api_key_here
STABILITY_API_KEY=your_stability_api_key_here

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_actual_secret_key_here
# STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here  # Optional - only needed for webhooks

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
```

## 3. Install Dependencies

### Backend
```bash
cd backend
pip install -r requirements.txt
```

The Stripe dependency has been added to `requirements.txt`.

### Frontend
The Stripe dependencies are already installed in your frontend.

## 4. Test the Integration

### Start the Backend
```bash
cd backend
python app.py
```

### Start the Frontend
```bash
cd frontend/style-ai
npm run dev
```

### Test Payment Flow
1. Register/Login to your app
2. Go to the payment page
3. Use Stripe's test card numbers:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - Use any future expiry date and any 3-digit CVC

## 5. Stripe Test Card Numbers (No Real Cards Needed!)

Stripe provides special test card numbers that work in test mode. These are **completely fake** and safe to use:

### ✅ Successful Payments
- **Visa**: `4242 4242 4242 4242`
- **Visa (Debit)**: `4000 0566 5566 5556`
- **Mastercard**: `5555 5555 5555 4444`
- **American Express**: `3782 822463 10005`
- **Discover**: `6011 1111 1111 1117`

### ❌ Declined Payments (for testing error handling)
- **Generic Decline**: `4000 0000 0000 0002`
- **Insufficient Funds**: `4000 0000 0000 9995`
- **Lost Card**: `4000 0000 0000 9987`
- **Stolen Card**: `4000 0000 0000 9979`

### 📅 Card Details
- **Expiry Date**: Any future date (e.g., `12/25`, `01/26`)
- **CVC**: Any 3 digits (e.g., `123`, `456`)
- **ZIP Code**: Any 5 digits (e.g., `12345`)

### 💡 Pro Tips
- These cards **only work in test mode** (with test keys)
- They **never charge real money**
- Perfect for testing your payment flow
- Use different cards to test different scenarios

## 6. What's Been Implemented

### Backend Endpoints
- `POST /auth/create-payment-intent` - Creates a Stripe payment intent
- `POST /auth/confirm-payment` - Confirms payment and adds credits
- `POST /auth/purchase-credits` - Legacy endpoint (simulated payment)

### Frontend Integration
- Stripe Elements for secure card input
- Payment form with proper validation
- Success/error handling
- Credit addition after successful payment

### Configuration
- Stripe keys loaded from environment variables
- Configurable credit packages (currently 25 credits for $5)
- Proper error handling and logging

## 7. Webhooks (Optional)

Webhooks are not required for basic payment processing, but they provide additional security and reliability. If you want to set up webhooks:

### Finding Webhook Secret
1. In your Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **"Add endpoint"** or select an existing webhook
3. The webhook secret will be shown in the webhook details (starts with `whsec_`)

### Basic Setup (No Webhooks Needed)
For your current implementation, you don't need webhooks. The payment confirmation happens directly in your frontend after Stripe processes the payment.

## 8. Going Live (Production)

When you're ready to go live:

1. **Switch to Live Mode** in your Stripe Dashboard
2. **Get Live Keys** (replace test keys with live ones)
3. **Update Environment Variables** with live keys
4. **Set up Webhooks** for production (optional but recommended)
5. **Test with Real Cards** (small amounts first)

## 9. Security Notes

- Never commit your `.env` files to version control
- Keep your secret keys secure
- Use HTTPS in production
- Validate all payments on the backend
- Consider implementing webhooks for additional security

## 10. Troubleshooting

### Common Issues
1. **"Invalid API Key"** - Check your Stripe keys are correct
2. **"No such payment_intent"** - Payment intent might have expired
3. **CORS errors** - Make sure your frontend URL is allowed in Stripe settings
4. **Environment variables not loading** - Restart your servers after adding .env files

### Debug Mode
Check the backend logs for detailed error messages. The app logs all Stripe operations.

## 11. Next Steps

- Set up Stripe webhooks for production
- Add more payment options (Apple Pay, Google Pay)
- Implement subscription plans
- Add payment history for users
- Set up proper error monitoring

Your Stripe integration is now ready to use! The payment flow will work seamlessly with your existing credit system.
