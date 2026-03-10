# 🚀 PDF Parser Service - Deployment Guide

## Quick Start (5 Minutes)

### Step 1: Push to GitHub

Open a terminal in the `parser-service` folder:

```bash
cd parser-service

# Initialize git
git init
git add .
git commit -m "PDF Parser Service"

# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/pdf-parser-service.git
git push -u origin main
```

### Step 2: Deploy to Render

1. **Go to** https://render.com and sign in

2. **Click "New +"** → **"Web Service"**

3. **Connect your repository**
   - Click "Connect a repository"
   - Select `pdf-parser-service`
   - Render auto-detects Python

4. **Configure** (use these exact settings):

   | Setting | Value |
   |---------|-------|
   | Name | `pdf-parser-service` |
   | Region | Choose closest to you |
   | Branch | `main` |
   | Root Directory | *(leave blank)* |
   | Runtime | `Python 3` |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn app:app` |
   | Instance Type | **Free** |

5. **Click "Create Web Service"**

6. **Wait 2-3 minutes** for deployment

7. **Copy your URL** (e.g., `https://pdf-parser-xyz.onrender.com`)

### Step 3: Test Your Service

```bash
# Health check
curl https://YOUR-SERVICE.onrender.com/health

# Test with a sample PDF
curl -X POST https://YOUR-SERVICE.onrender.com/parse \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'
```

Expected response:
```json
{
  "success": true,
  "text": "Dummy PDF file...",
  "pages": 1,
  ...
}
```

### Step 4: Update Telegram Bot

1. **Edit `wrangler.jsonc`** in your bot project:
   ```json
   {
     "vars": {
       "PARSER_API_URL": "https://YOUR-SERVICE.onrender.com"
     }
   }
   ```

2. **Redeploy your bot**:
   ```bash
   npm run deploy
   ```

### Step 5: Test End-to-End

1. **Upload a PDF** to your Telegram group
2. **Wait for**: "✅ PDF processed successfully!"
3. **Ask**: "What is this document about?"
4. **Bot should answer** with actual content!

---

## Troubleshooting

### "External parser failed"

Check your Render service:
1. Go to Render dashboard
2. Click your service
3. Click **"Logs"** tab
4. Look for errors

Common issues:
- Service not deployed correctly
- Wrong URL in `wrangler.jsonc`
- Service is sleeping (first request after sleep takes ~30s)

### PDF still not extracting

The PDF might be:
- Scanned/image-based (needs OCR)
- Password protected
- Corrupted

Try with a different PDF first.

### Service is slow

Free tier services sleep after 15 minutes of inactivity.
- First request: ~30 seconds (waking up)
- Subsequent requests: <2 seconds

This is normal for free tier.

---

## Cost

**$0/month** for:
- 750 hours/month (enough for always-on)
- 512MB RAM
- Unlimited requests

For 10-50 PDFs/day, you'll use <10% of free tier.

---

## Next Steps

### Optional Improvements

1. **Add authentication** (API key) to protect your service
2. **Enable auto-deploy** from GitHub for automatic updates
3. **Add monitoring** (Render has built-in metrics)
4. **Upgrade to paid tier** ($7/month) for faster performance

### Using the Service

Your parser service is now available at:
```
https://YOUR-SERVICE.onrender.com
```

Endpoints:
- `GET /health` - Health check
- `POST /parse` - Extract text from PDF
- `GET /parse/info` - Service information

---

## Support

If you get stuck:
1. Check Render logs
2. Test locally first: `python app.py`
3. Verify PDF URL is publicly accessible
4. Check bot's `wrangler.jsonc` has correct URL
