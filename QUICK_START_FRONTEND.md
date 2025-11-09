# Quick Start - Frontend

## ✅ Everything is Ready!

I've configured the frontend to work with your API. Here's how to start it:

## Step 1: Start the Frontend Server

Run this command in your terminal:

```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
./start-frontend.sh
```

Or manually:
```bash
cd frontend
python3 -m http.server 5173
```

## Step 2: Open in Browser

Once the server is running, open your browser and go to:

**🔗 http://localhost:5173/diagnosis.html**

This is the starting point of the application.

## Step 3: Use the Application

### Application Flow:

1. **Diagnosis Page** (`diagnosis.html`)
   - Answer questions about your health and fitness goals
   - Click "Yap" button to chat with AI about questions
   - Click "Next" to proceed through questions
   - When done, it will redirect to flavor page

2. **Flavor Page** (`flavor.html`)
   - Set your flavor preferences
   - Answer questions about cuisines, spices, etc.
   - Lock your flavor profile when done

3. **Recipe Generation** (`recipe.html`)
   - Lock evaluation
   - Lock flavor
   - Compile analysis
   - Generate recipes!

## What I Fixed

✅ Updated API endpoints to use `http://localhost:8000`
✅ Copied JSON question files to frontend directory
✅ Fixed relative paths for questions files
✅ Created startup script for easy frontend launch

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
1. Make sure `.env` has: `CORS_ORIGINS=http://localhost:5173`
2. Restart API: `sudo docker compose restart api`

### API Not Responding
Check if API is running:
```bash
curl http://localhost:8000/health
```

Should return: `{"ok":true}`

### Port Already in Use
If port 5173 is busy:
```bash
# Use a different port
cd frontend
python3 -m http.server 5174
# Then access at http://localhost:5174/diagnosis.html
```

### Check Browser Console
Open browser developer tools (F12) and check the Console tab for any errors.

## Next Steps

1. ✅ Start frontend: `./start-frontend.sh`
2. ✅ Open browser: http://localhost:5173/diagnosis.html
3. ✅ Start answering questions!
4. ✅ Enjoy your AI Recipe Generator! 🍳

## Need Help?

- Check API logs: `sudo docker compose logs -f api`
- Check browser console for errors
- Verify API is running: `curl http://localhost:8000/health`

Enjoy! 🎉

