# Frontend Guide

## Quick Start

The frontend is a simple static HTML/CSS/JS application. Here's how to start it:

### Option 1: Use the Startup Script (Easiest)

```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
./start-frontend.sh
```

### Option 2: Manual Start

```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai/frontend
python3 -m http.server 5173
```

## Access the Frontend

Once the server is running, open these URLs in your browser:

### Main Pages:
- **Diagnosis** (Start here): http://localhost:5173/diagnosis.html
- **Flavor Preferences**: http://localhost:5173/flavor.html
- **Recipe Generation**: http://localhost:5173/recipe.html
- **Index**: http://localhost:5173/index.html

### Other Pages:
- **Taste**: http://localhost:5173/taste.html
- **Recipe Full**: http://localhost:5173/recipefull.html
- **Recipes Index**: http://localhost:5173/recipes/index.html

## Application Flow

1. **Start with Diagnosis** (`diagnosis.html`)
   - Answer questions about your health, fitness goals, etc.
   - Use the "Yap" button for conversational interactions
   - Click "Next" to proceed through questions

2. **Flavor Preferences** (`flavor.html`)
   - Set your flavor preferences
   - Lock your flavor profile when done

3. **Recipe Generation** (`recipe.html`)
   - Generate personalized recipes based on your profile
   - View and save recipes

## Important Notes

### Backend Connection
The frontend connects to the API at: `http://localhost:8000`

Make sure:
- ✅ Backend API is running (`curl http://localhost:8000/health` should work)
- ✅ CORS is configured correctly (already set in `backend/core/config.py`)
- ✅ The API is accessible from your browser

### API Endpoints Used
- `/api/session/*` - Session management
- `/api/diagnosis/*` - Diagnosis questions
- `/api/flavor/*` - Flavor preferences
- `/api/yap/*` - Conversational AI
- `/api/analysis/*` - Analysis compilation
- `/api/recipes/*` - Recipe generation

## Troubleshooting

### Frontend Server Won't Start
```bash
# Check if port is in use
lsof -i :5173

# Use a different port
python3 -m http.server 5174
# Then access at http://localhost:5174/diagnosis.html
```

### API Connection Errors
- Check browser console (F12) for errors
- Verify API is running: `curl http://localhost:8000/health`
- Check CORS settings in `backend/core/config.py`

### CORS Errors
If you see CORS errors in the browser console:
1. Check `.env` file has: `CORS_ORIGINS=http://localhost:5173`
2. Restart the API: `sudo docker compose restart api`

## Development Tips

### Running Both Frontend and Backend

**Terminal 1 - Backend:**
```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
# Backend should already be running via Docker
# Check status: sudo docker compose ps
```

**Terminal 2 - Frontend:**
```bash
cd /home/straycat/Coding/meenaapp/ai-recipe-genai
./start-frontend.sh
```

### Viewing Logs
```bash
# Backend logs
sudo docker compose logs -f api

# Frontend - check browser console (F12)
```

### Making Changes
- Frontend changes: Just refresh the browser (no restart needed)
- Backend changes: Restart API container: `sudo docker compose restart api`

## Next Steps

1. ✅ Start frontend server: `./start-frontend.sh`
2. ✅ Open http://localhost:5173/diagnosis.html in your browser
3. ✅ Start answering questions!
4. ✅ Follow the flow through diagnosis → flavor → recipes

Enjoy your AI Recipe Generator! 🍳

