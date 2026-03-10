# PDF Parser Service

A Python Flask service that extracts text from PDF files using the `pypdf` library.

## Features

- ✅ Extracts text from PDFs (including compressed/FlateDecode streams)
- ✅ Returns structured JSON with text, page count, and metadata
- ✅ Handles 99% of text-based PDFs correctly
- ✅ Free to host on Render/Railway/Hugging Face
- ✅ Supports both URL and base64 input

## API Endpoints

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "message": "PDF Parser Service is running",
  "version": "1.0.0"
}
```

### `POST /parse`

Extract text from a PDF.

**Request Body:**
```json
{
  "pdf_url": "https://example.com/document.pdf"
}
```

Or with base64:
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9..."
}
```

**Success Response (200):**
```json
{
  "success": true,
  "text": "Full extracted text from all pages...",
  "pages": 6,
  "is_scanned": false,
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "subject": "",
    "creator": "",
    "producer": ""
  },
  "chunks": [
    {
      "page": 1,
      "text": "Text from page 1...",
      "char_count": 1500
    },
    {
      "page": 2,
      "text": "Text from page 2...",
      "char_count": 1200
    }
  ]
}
```

**Error Response (400/500):**
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

### `GET /parse/info`

Service information and limits.

---

## Local Development

### Prerequisites

- Python 3.11 or higher
- pip

### Setup

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python app.py
```

The service will start on `http://localhost:5000`

### Test Locally

```bash
# Health check
curl http://localhost:5000/health

# Test with a PDF URL
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://example.com/test.pdf"}'

# Test with a local PDF (convert to base64 first)
base64 -i test.pdf | pbcopy  # Copy base64 to clipboard
# Then paste into JSON:
curl -X POST http://localhost:5000/parse \
  -H "Content-Type: application/json" \
  -d '{"pdf_base64": "JVBERi0xLjQK..."}'
```

---

## Deploy to Render (Free)

### Step 1: Prepare Your Code

**Option A: Using GitHub (Recommended)**

1. Create a new GitHub repository
2. Push the `parser-service` folder contents:
   ```bash
   cd parser-service
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/pdf-parser-service.git
   git push -u origin main
   ```

**Option B: Direct Upload to Render**

1. Zip the `parser-service` folder
2. Upload directly during Render setup

### Step 2: Create Render Web Service

1. **Go to Render**: https://render.com
2. **Sign in** with your GitHub account
3. **Click "New +"** → **"Web Service"**

### Step 3: Configure Service

**If using GitHub:**
- Click **"Connect a repository"**
- Select your `pdf-parser-service` repository
- Render auto-detects Python

**If uploading directly:**
- Choose **"Deploy from Git"** or **"Deploy from Disk"**
- Follow upload instructions

**Configuration:**
| Setting | Value |
|---------|-------|
| **Name** | `pdf-parser-service` (or your choice) |
| **Region** | Choose closest to you |
| **Branch** | `main` |
| **Root Directory** | (leave blank) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | **Free** |
| **Auto-Deploy** | ✅ Enabled (for GitHub) |

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait 2-3 minutes for deployment
3. Once deployed, you'll see:
   - **Service URL**: `https://pdf-parser-xyz.onrender.com`
   - **Status**: Live

### Step 5: Test Deployment

```bash
# Health check
curl https://pdf-parser-xyz.onrender.com/health

# Test parse
curl -X POST https://pdf-parser-xyz.onrender.com/parse \
  -H "Content-Type: application/json" \
  -d '{"pdf_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"}'
```

---

## Deploy to Railway (Alternative)

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway auto-detects Python
6. Add environment variables if needed
7. Set start command: `gunicorn app:app`
8. Deploy

---

## Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE_MB` | `10` | Maximum PDF file size in MB |
| `TIMEOUT_SECONDS` | `30` | Request timeout in seconds |
| `PORT` | `5000` | Port to listen on (set by Render) |

---

## Usage with Telegram Study Bot

Once deployed, update your bot's `wrangler.jsonc`:

```json
{
  "vars": {
    "PARSER_API_URL": "https://pdf-parser-xyz.onrender.com"
  }
}
```

Then redeploy your bot. The bot will automatically use the external parser for all PDF uploads.

---

## Troubleshooting

### "No text could be extracted"

The PDF is likely:
- A scanned image (needs OCR)
- Contains only images/diagrams
- Encrypted or password-protected

### Service is slow to respond

- Free tier services may sleep after inactivity
- First request after sleep takes ~30 seconds
- Subsequent requests are fast (<2 seconds)

### Deployment fails

Check logs on Render:
1. Go to your service dashboard
2. Click **"Logs"** tab
3. Look for error messages

Common issues:
- Missing `requirements.txt`
- Wrong start command
- Python version mismatch

---

## Cost Estimate

| Platform | Cost | Limits |
|----------|------|--------|
| **Render Free** | $0 | 750 hours/month, 512MB RAM |
| **Railway** | ~$0-5 | Pay per usage, $5 credit |
| **Hugging Face Spaces** | $0 | CPU basic, 16GB storage |

For 10-50 PDFs/day, all free tiers are sufficient.

---

## License

MIT License - Feel free to use and modify.
