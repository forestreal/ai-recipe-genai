# Setting Up Google Gemini API Key

## Why You Need This

The AI features (chat, recipe generation, analysis) require a Google Gemini API key to work. Without it, you'll get errors when trying to:
- Use the "Yap" chat feature
- Generate recipes
- Compile analysis

## How to Get Your API Key

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey

2. **Sign in** with your Google account

3. **Create a new API key**:
   - Click "Create API Key"
   - Choose "Create API key in new project" (or select existing project)
   - Copy the API key that's generated

4. **Add it to your `.env` file**:
   ```bash
   cd /home/straycat/Coding/meenaapp/ai-recipe-genai
   nano .env
   ```
   
   Find this line:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```
   
   Replace `your-api-key-here` with your actual API key:
   ```
   GOOGLE_API_KEY=AIzaSy...your-actual-key-here
   ```
   
   Save and exit (Ctrl+X, then Y, then Enter)

5. **Restart the API** to apply the new key:
   ```bash
   sudo docker compose restart api
   ```

## Verify It's Working

After restarting, test the API:
```bash
curl http://localhost:8000/health
```

Then try using the "Yap" feature in the frontend - it should work now!

## Troubleshooting

### "Missing GOOGLE_API_KEY" Error
- Make sure you've updated `.env` with your actual API key
- Make sure you restarted the API container
- Check that the key doesn't have extra spaces or quotes

### "API key invalid" Error
- Make sure you copied the entire API key
- Check that the key is active in Google AI Studio
- Verify there are no extra characters

### Rate Limits
Google Gemini API has rate limits on free tier. If you hit limits:
- Wait a few minutes and try again
- Consider upgrading to a paid plan if needed

## Cost

Google Gemini API has a **free tier** with generous limits for development and testing. Check current pricing at: https://ai.google.dev/pricing

## Security Note

⚠️ **Never commit your `.env` file to git!** It contains your API key. The `.env` file should already be in `.gitignore`.

