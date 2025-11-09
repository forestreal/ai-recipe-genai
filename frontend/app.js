// formatted: small non-functional formatting change
let questions = [];
let idx = 0;
let layer = "diagnosis";
const API_BASE = 'http://localhost:8000';

async function initDiagnosis(){
  layer = "diagnosis";
  questions = await (await fetch('./questions.json')).json();
  idx = 0; renderSlide(); bindControls();
}
async function initFlavor(){
  layer = "flavor";
  questions = await (await fetch('./questions_flavor.json')).json();
  idx = 0; renderSlide(); bindControls();
}
function bindControls(){
  document.getElementById('yapBtn').onclick = openYap;
  document.getElementById('nextBtn').onclick = nextSlide;
}
function renderSlide(){
  const q = questions[idx];
  const el = document.getElementById('slide');
  const reply = document.getElementById('reply'); reply.textContent = '';
  document.getElementById('nextBtn').disabled = true;

  if(!q){
    if(layer==='diagnosis'){ window.location.href = 'flavor.html'; }
    else { window.location.href = 'index.html'; }
    return;
  }
  let html = `<div class="q"><div class="qtext">${q.question}</div>`;
  if(q.type === 'choice'){
    html += '<div class="opts">' + (q.options||[]).map((o,i)=>`<button class="opt" data-i="${i}">${o}</button>`).join('') + '</div>';
  } else if (q.type === 'number' || q.type === 'text'){
    html += `<input id="ans" type="${q.type==='number'?'number':'text'}" placeholder="Type here"/> <button id="commit">Commit</button>`;
  } else if (q.type === 'llm_trigger'){
    html += `<div class="muted">(A short vibe line will be used later.)</div>`;
    document.getElementById('nextBtn').disabled = false;
  }
  html += '</div>';
  el.innerHTML = html;

  if(q.type === 'choice'){
    for(const b of document.querySelectorAll('.opt')){
      b.onclick = async (e)=>{
        const i = +e.target.dataset.i;
        const val = q.options[i];
        await fetch(layer==='diagnosis'? `${API_BASE}/api/diagnosis/answer`:`${API_BASE}/api/flavor/answer`,{
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({question_id: q.id, value: val})
        });
        document.getElementById('nextBtn').disabled = false;
      };
    }
  } else if (q.type === 'number' || q.type === 'text'){
    document.getElementById('commit').onclick = async ()=>{
      const val = document.getElementById('ans').value.trim();
      if(!val) return;
      await fetch(layer==='diagnosis'? `${API_BASE}/api/diagnosis/answer`:`${API_BASE}/api/flavor/answer`,{
        method:'POST', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({question_id: q.id, value: val})
      });
      document.getElementById('nextBtn').disabled = false;
    };
  }
}
async function openYap(){
  const q = questions[idx];
  const user = prompt('Talk to the AI (≤100 words reply).');
  if(!user) return;
  
  const replyEl = document.getElementById('reply');
  replyEl.textContent = 'Thinking...';
  
  try {
    const res = await fetch(`${API_BASE}/api/yap/answer`,{
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ question: q, user_message: user, context: {} })
    });
    
    if (!res.ok) {
      const error = await res.json();
      if (res.status === 503 && error.detail && error.detail.includes('API key')) {
        replyEl.innerHTML = `❌ <strong>API Key Missing!</strong><br><br>${error.detail}<br><br>See SETUP_API_KEY.md for instructions.`;
      } else {
        replyEl.textContent = `Error: ${error.detail || 'Unknown error'}`;
      }
      return;
    }
    
    const data = await res.json();
    replyEl.textContent = data.display_reply;
    if(data.commit && data.commit.applied){ document.getElementById('nextBtn').disabled = false; }
  } catch (error) {
    replyEl.textContent = `Connection error: ${error.message}`;
  }
}
function nextSlide(){ idx++; renderSlide(); }

function showStatus(message, type = 'info') {
  const statusEl = document.getElementById('status');
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  statusEl.style.display = 'block';
  setTimeout(() => {
    if (type !== 'error') statusEl.style.display = 'none';
  }, 5000);
}

function updateStep(stepId, completed) {
  const stepEl = document.getElementById(stepId);
  if (!stepEl) return;
  if (completed) {
    stepEl.classList.remove('pending');
    stepEl.classList.add('completed');
  } else {
    stepEl.classList.remove('completed');
    stepEl.classList.add('pending');
  }
}

async function initGenerate(){
  // Lock Evaluation
  document.getElementById('lockEval').onclick = async ()=>{
    const btn = document.getElementById('lockEval');
    const statusEl = document.getElementById('eval-status');
    btn.disabled = true;
    statusEl.textContent = ' Locking...';
    try {
      const res = await fetch(`${API_BASE}/api/diagnosis/evaluate`,{
        method:'POST', 
        headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({force:false})
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to lock evaluation');
      }
      const data = await res.json();
      statusEl.textContent = ' ✅ Locked!';
      updateStep('step-eval', true);
      showStatus('Evaluation locked successfully!', 'success');
      document.getElementById('lockFlavor').disabled = false;
      document.getElementById('compileAnalysis').disabled = false;
    } catch (error) {
      statusEl.textContent = ' ❌ Error';
      showStatus(`Error: ${error.message}. Make sure you've completed the diagnosis questions first!`, 'error');
      btn.disabled = false;
    }
  };

  // Lock Flavor
  document.getElementById('lockFlavor').onclick = async ()=>{
    const btn = document.getElementById('lockFlavor');
    const statusEl = document.getElementById('flavor-status');
    btn.disabled = true;
    statusEl.textContent = ' Locking...';
    try {
      const res = await fetch(`${API_BASE}/api/flavor/lock`,{
        method:'POST', 
        headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({force:false})
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to lock flavor');
      }
      const data = await res.json();
      statusEl.textContent = ' ✅ Locked!';
      updateStep('step-flavor', true);
      showStatus('Flavor profile locked successfully!', 'success');
      document.getElementById('compileAnalysis').disabled = false;
    } catch (error) {
      statusEl.textContent = ' ❌ Error';
      showStatus(`Error: ${error.message}. Make sure you've completed the flavor questions first!`, 'error');
      btn.disabled = false;
    }
  };

  // Compile Analysis
  document.getElementById('compileAnalysis').onclick = async ()=>{
    const btn = document.getElementById('compileAnalysis');
    const statusEl = document.getElementById('analysis-status');
    btn.disabled = true;
    statusEl.textContent = ' Compiling...';
    try {
      const res = await fetch(`${API_BASE}/api/analysis/compile`,{method:'POST'});
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to compile analysis');
      }
      const data = await res.json();
      statusEl.textContent = ' ✅ Compiled!';
      updateStep('step-analysis', true);
      showStatus('Analysis compiled successfully!', 'success');
      document.getElementById('genBtn').disabled = false;
    } catch (error) {
      statusEl.textContent = ' ❌ Error';
      let errorMsg = error.message;
      if (error.message && error.message.includes('API key')) {
        errorMsg = 'Google Gemini API key is not configured. See SETUP_API_KEY.md for instructions.';
      }
      showStatus(`Error: ${errorMsg}. Make sure evaluation and flavor are locked first!`, 'error');
      btn.disabled = false;
    }
  };

  // Generate Recipes
  document.getElementById('genBtn').onclick = async ()=>{
    const btn = document.getElementById('genBtn');
    const statusEl = document.getElementById('generate-status');
    const outEl = document.getElementById('out');
    btn.disabled = true;
    statusEl.textContent = ' Generating...';
    outEl.textContent = 'Generating your personalized recipes... This may take a moment.';
    try {
      const res = await fetch(`${API_BASE}/api/recipes/generate`,{
        method:'POST', 
        headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify({count:3, meals:["lunch","dinner","snack"]})
      });
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to generate recipes');
      }
      const recipes = await res.json();
      statusEl.textContent = ' ✅ Generated!';
      updateStep('step-generate', true);
      showStatus('Recipes generated successfully!', 'success');
      
      // Format recipes nicely
      if (Array.isArray(recipes) && recipes.length > 0) {
        outEl.innerHTML = formatRecipesHTML(recipes);
      } else {
        outEl.textContent = JSON.stringify(recipes, null, 2);
      }
    } catch (error) {
      statusEl.textContent = ' ❌ Error';
      let errorMsg = `Error generating recipes: ${error.message}`;
      
      // Check if it's an API key error
      if (error.message && error.message.includes('API key')) {
        errorMsg = `❌ Google Gemini API Key Not Configured!\n\n` +
          `The AI features require a Google Gemini API key.\n\n` +
          `To fix this:\n` +
          `1. Get your API key from: https://makersuite.google.com/app/apikey\n` +
          `2. Edit .env file and set: GOOGLE_API_KEY=your-actual-key\n` +
          `3. Restart API: sudo docker compose restart api\n\n` +
          `See SETUP_API_KEY.md for detailed instructions.`;
      } else {
        errorMsg += `\n\nMake sure you've:\n1. Completed diagnosis questions\n2. Completed flavor preferences\n3. Locked evaluation\n4. Locked flavor\n5. Compiled analysis`;
      }
      
      outEl.textContent = errorMsg;
      showStatus(`Error: ${error.message}`, 'error');
      btn.disabled = false;
    }
  };

  // Dev-only: generate a single demo recipe from the debug endpoint and display it
  const devBtn = document.getElementById('devGenBtn');
  if (devBtn) {
    devBtn.onclick = async () => {
      const outEl = document.getElementById('out');
      const statusEl = document.getElementById('generate-status');
      devBtn.disabled = true;
      statusEl.textContent = ' Generating (demo)...';
      outEl.textContent = 'Fetching demo recipe...';
      try {
        const res = await fetch(`${API_BASE}/api/debug/generate`,{
          method: 'POST', headers: {'Content-Type':'application/json'},
          body: JSON.stringify({count:1, meals:['lunch']})
        });
        if (!res.ok) {
          const err = await res.text();
          throw new Error(err || `Status ${res.status}`);
        }
        const recipes = await res.json();
        statusEl.textContent = ' ✅ Demo generated';
        showStatus('Demo recipe generated', 'success');
        if (Array.isArray(recipes) && recipes.length > 0) {
          outEl.innerHTML = formatRecipesHTML(recipes);
        } else {
          outEl.textContent = JSON.stringify(recipes, null, 2);
        }
      } catch (e) {
        statusEl.textContent = ' ❌ Error';
        outEl.textContent = `Error fetching demo recipe: ${e.message}`;
        showStatus(`Error: ${e.message}`, 'error');
      } finally {
        devBtn.disabled = false;
      }
    };
  }
}

// Helper: build HTML string of recipe cards
function formatRecipesHTML(recipes) {
  if (!Array.isArray(recipes)) return `<div>${String(recipes)}</div>`;
  const escape = (s) => String(s || '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
  let html = '<div class="recipes-grid">';
  recipes.forEach((recipe, idx) => {
    html += `<article class="recipe-card">`;
    html += `<h2 class="r-title">${escape(recipe.title || 'Untitled')}</h2>`;
    html += `<div class="r-meta">${escape(recipe.cuisine || 'N/A')} • ${escape(recipe.meal_type || 'N/A')} • Prep ${escape(recipe.prep_time || 'N/A')}m • ${escape(recipe.difficulty || 'N/A')}</div>`;
    if (recipe.ingredients && recipe.ingredients.length) {
      html += `<h3>Ingredients</h3><ul class="r-ings">`;
      recipe.ingredients.forEach(ing => {
        const qty = ing.quantity !== undefined ? escape(ing.quantity) : '';
        const unit = ing.unit ? ` ${escape(ing.unit)}` : '';
        html += `<li>${qty}${unit} — ${escape(ing.item || '')}</li>`;
      });
      html += `</ul>`;
    }
    if (recipe.instructions && recipe.instructions.length) {
      html += `<h3>Instructions</h3><ol class="r-insts">`;
      recipe.instructions.forEach(inst => {
        html += `<li>${escape(inst)}</li>`;
      });
      html += `</ol>`;
    }
    if (recipe.macros) {
      html += `<div class="r-macros"><strong>Nutrition</strong>: ${escape(recipe.macros.calories || 'N/A')} kcal — `;
      html += `P ${escape(recipe.macros.protein_g || 'N/A')}g • C ${escape(recipe.macros.carbs_g || 'N/A')}g • F ${escape(recipe.macros.fat_g || 'N/A')}g`;
      html += `</div>`;
    }
    if (recipe.notes) html += `<div class="r-notes"><em>${escape(recipe.notes)}</em></div>`;
    html += `</article>`;
  });
  html += '</div>';
  // Add compact CSS to make cards look nicer (scoped inline so no file edits needed)
  html += `<style>
    .recipes-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}
    .recipe-card{background:#0f1318;border:1px solid #222831;padding:16px;border-radius:8px}
    .r-title{margin:0 0 6px;color:#60a5fa}
    .r-meta{font-size:0.9rem;color:#9ad;margin-bottom:8px}
    .r-ings{margin:6px 0 12px 18px}
    .r-insts{margin:6px 0 12px 18px}
    .r-macros{margin-top:8px;color:#cbe7d6}
    .r-notes{margin-top:8px;color:#cbd5e1}
  </style>`;
  return html;
}