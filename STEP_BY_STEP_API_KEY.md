# Step-by-Step: Set Up Google Gemini API Key

## Current Status
Your `.env` file still has: `GOOGLE_API_KEY=your-api-key-here`

This is a placeholder. You need to replace it with your actual API key.

---

## Step 1: Get Your API Key

1. **Open your browser** and go to: **https://makersuite.google.com/app/apikey**

2. **Sign in** with your Google account (if not already signed in)

3. **Click "Create API Key"** button
   - You might see "Get API Key" or "Create API Key in new project"
   - Click it

4. **Copy the API key** that appears
   - It will look like: `AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz1234567`
   - Click the copy button or select and copy it

---

## Step 2: Edit the .env File

Open a terminal and run:

```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
nano .env
```

### In the nano editor:

1. **Find this line** (use Ctrl+W to search for "GOOGLE_API_KEY"):
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

2. **Delete** `your-api-key-here` and **paste your actual API key**:
   ```
   GOOGLE_API_KEY=AIzaSy...your-actual-key-here
   ```

3. **Make sure**:
   - No quotes around the key
   - No spaces before or after the `=`
   - The key is on one line

4. **Save the file**:
   - Press `Ctrl+X` to exit
   - Press `Y` to confirm save
   - Press `Enter` to confirm filename

---

## Step 3: Restart the API

After saving the `.env` file, restart the API container:

```bash
sudo docker compose restart api
```

Wait 5-10 seconds for it to restart.

---

## Step 4: Verify It Works

1. **Refresh your browser** at http://localhost:5173/diagnosis.html

2. **Try the "Yap" button** - it should work now!

3. **Or test with curl**:
   ```bash
   curl http://localhost:8000/health
   ```

---

## Quick Check Script

You can also use the helper script:

```bash
./UPDATE_API_KEY.sh
```

This will guide you through the process.

---

## Common Mistakes

❌ **Wrong**: `GOOGLE_API_KEY="AIzaSy..."`
✅ **Right**: `GOOGLE_API_KEY=AIzaSy...`

❌ **Wrong**: `GOOGLE_API_KEY = AIzaSy...` (spaces around =)
✅ **Right**: `GOOGLE_API_KEY=AIzaSy...`

❌ **Wrong**: Forgetting to restart the API
✅ **Right**: Always restart after changing .env

---

## Still Not Working?

1. **Check the .env file**:
   ```bash
   cat .env | grep GOOGLE_API_KEY
   ```
   Should show your actual key, not "your-api-key-here"

2. **Check API logs**:
   ```bash
   sudo docker compose logs api --tail 20
   ```

3. **Verify the key is being read**:
   ```bash
   sudo docker compose exec api printenv | grep GOOGLE
   ```

---

## Need Help?

If you're having trouble:
- Make sure you copied the entire API key
- Check for typos
- Make sure there are no extra spaces
- Restart the API after making changes

