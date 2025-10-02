# 🚀 Deployment Guide

This guide will help you deploy the AI Photo Restoration Space to Hugging Face Spaces.

## 📋 Prerequisites

- Hugging Face account (free)
- Basic understanding of Git
- Your own Stripe account (for payments)
- Your own Ko-fi account (optional, for tips)

## 🎯 Step-by-Step Deployment

### 1. Prepare Your Space

1. **Create a new Space on Hugging Face:**
   - Go to https://huggingface.co/spaces
   - Click "Create New Space"
   - Choose a name (e.g., "ai-photo-restoration")
   - Select "Docker" as the SDK
   - Choose "Public" visibility
   - Click "Create Space"

### 2. Customize Your Configuration

Before deploying, customize these files:

#### Update Payment Links

**In `app.py`:**
```python
# Replace with your actual Stripe payment link
STRIPE_PAYMENT_URL = "https://buy.stripe.com/your-actual-link"

# Replace with your actual Ko-fi link
KOFI_URL = "https://ko-fi.com/your-actual-username"
```

#### Update README.md

Replace all instances of:
- `your-username` with your Hugging Face username
- `your-space-name` with your chosen space name
- `yourname` with your actual username in various links

### 3. Deploy to Hugging Face

**Option A: Using Git (Recommended)**

```bash
# Clone your newly created space
git clone https://huggingface.co/spaces/your-username/your-space-name
cd your-space-name

# Copy all files from this project
cp -r /path/to/this/project/* .

# Add all files
git add .

# Commit and push
git commit -m "Initial deployment"
git push
```

**Option B: Upload via Web Interface**

1. Go to your Space's "Files" tab
2. Upload all files from this project
3. The Space will automatically rebuild

### 4. Configure Your Space

#### Set Environment Variables

1. Go to your Space's "Settings" tab
2. Scroll to "Variables and secrets"
3. Add these environment variables:

```bash
# Required for CPU-only operation
CUDA_VISIBLE_DEVICES=""
DEVICE="cpu"

# Optional: Custom payment links
STRIPE_PAYMENT_URL="https://buy.stripe.com/your-link"
KOFI_URL="https://ko-fi.com/yourname"
```

#### Set Hardware

1. In Space Settings, go to "Hardware"
2. Select "CPU basic" (this is optimized for our app)
3. Save changes

### 5. Set Up Payments

#### Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Create a payment link:
   - Go to "Payments" → "Payment links"
   - Click "Create payment link"
   - Set price to $0.99
   - Add product description
   - Set redirect URL to your Space URL
   - Copy the payment link
3. Update `STRIPE_PAYMENT_URL` in your code

#### Ko-fi Setup (Optional)

1. Create a Ko-fi account at https://ko-fi.com
2. Customize your page
3. Copy your Ko-fi link
4. Update `KOFI_URL` in your code

### 6. Test Your Deployment

1. Wait for the Space to build (2-3 minutes)
2. Visit your Space URL
3. Upload a test photo
4. Verify the restoration works
5. Test the payment button

## 🔧 Troubleshooting

### Common Issues

#### 1. Build Failures

**Problem:** Space fails to build
**Solution:** 
- Check the build logs in Space settings
- Ensure all files are uploaded correctly
- Verify Docker configuration

#### 2. Model Loading Issues

**Problem:** Models fail to download or load
**Solution:**
- Check internet connectivity
- Verify model URLs in the code
- Check available disk space

#### 3. Memory Issues

**Problem:** Out of memory errors
**Solution:**
- Ensure you're using CPU-basic hardware
- Check that `CUDA_VISIBLE_DEVICES=""` is set
- Monitor memory usage in Space settings

#### 4. Payment Link Issues

**Problem:** Payment button doesn't work
**Solution:**
- Verify your Stripe payment link is correct
- Check that the link opens in a new tab
- Test the payment flow manually

### Performance Optimization

#### Reduce Cold Start Time

1. **Pre-download models:**
   - Models are downloaded on first use
   - This causes a delay for the first user
   - Consider adding a startup script to pre-load models

2. **Optimize caching:**
   - The app caches results for 24 hours
   - This speeds up repeated requests
   - Monitor cache size in the outputs directory

#### Monitor Resource Usage

1. Check the "Analytics" tab in your Space settings
2. Monitor:
   - CPU usage
   - Memory consumption
   - Request count
   - Error rate

## 📈 Scaling Considerations

### Traffic Management

- Hugging Face Spaces automatically scales
- CPU-basic tier handles moderate traffic
- Consider upgrading hardware if needed

### Cost Management

- Hugging Face Spaces are free for public repos
- Stripe charges ~2.9% + 30¢ per transaction
- Ko-fi takes 0% of tips (payment processor fees apply)

## 🔒 Security Best Practices

1. **Environment Variables:**
   - Never hardcode API keys
   - Use Space environment variables
   - Keep `.env` files out of version control

2. **File Uploads:**
   - Validate file types and sizes
   - Scan for malicious content
   - Limit upload frequency

3. **Payment Security:**
   - Use HTTPS only
   - Verify webhook signatures
   - Monitor for fraudulent transactions

## 🎯 Next Steps

After successful deployment:

1. **Test thoroughly** with various photo types
2. **Share on social media** to get initial users
3. **Collect feedback** and improve the app
4. **Monitor analytics** to understand usage patterns
5. **Consider premium features** for future updates

## 📞 Getting Help

If you encounter issues:

1. Check the [Hugging Face Spaces documentation](https://huggingface.co/docs/hub/spaces)
2. Search existing issues in this repository
3. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Space URL (if applicable)

## 🎉 Success!

Your AI Photo Restoration Space is now live! Share it with friends and family to help them restore their precious memories.

---

**Need help?** Open an issue or reach out through the support channels listed in the main README.