# Quick API Key Setup

## Step 1: Get Your API Key

1. **Go to**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click "Create API Key"** (or "Get API Key")
4. **Copy the key** that appears (starts with `AIzaSy...`)

## Step 2: Add It to .env

Open the `.env` file:

```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
nano .env
```

Find this line:
```
GOOGLE_API_KEY=your-api-key-here
```

Replace it with your actual key:
```
GOOGLE_API_KEY=AIzaSy...your-actual-key-here
```

**Important**: 
- Don't add quotes around the key
- Don't add spaces
- Make sure there are no extra characters

Save and exit:
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

## Step 3: Restart the API

```bash
sudo docker compose restart api
```

Wait 5-10 seconds for it to restart.

## Step 4: Test It

Try using the "Yap" button in the frontend - it should work now!

## Troubleshooting

### "API key invalid" error
- Make sure you copied the entire key
- Check for extra spaces or characters
- Make sure the key is active in Google AI Studio

### Still getting "API key not configured"
- Make sure you saved the `.env` file
- Make sure you restarted the API: `sudo docker compose restart api`
- Check the key is correct: `cat .env | grep GOOGLE_API_KEY`

### Rate limit errors
- Google Gemini has rate limits on the free tier
- Wait a few minutes and try again
- Check your usage at: https://makersuite.google.com/app/apikey

## Cost

✅ **Free tier available!** Google Gemini API has generous free limits for development.

Check current pricing: https://ai.google.dev/pricing

