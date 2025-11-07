let questions = [];
let idx = 0;
let layer = "diagnosis";

async function initDiagnosis(){
  layer = "diagnosis";
  questions = await (await fetch('/questions.json')).json();
  idx = 0; renderSlide(); bindControls();
}
async function initFlavor(){
  layer = "flavor";
  questions = await (await fetch('/questions_flavor.json')).json();
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
    if(layer==='diagnosis'){ window.location.href = '/flavor.html'; }
    else { window.location.href = '/index.html'; }
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
        await fetch(layer==='diagnosis'? '/api/diagnosis/answer':'/api/flavor/answer',{
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
      await fetch(layer==='diagnosis'? '/api/diagnosis/answer':'/api/flavor/answer',{
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
  const res = await fetch('/api/yap/answer',{
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ question: q, user_message: user, context: {} })
  });
  const data = await res.json();
  document.getElementById('reply').textContent = data.display_reply;
  if(data.commit && data.commit.applied){ document.getElementById('nextBtn').disabled = false; }
}
function nextSlide(){ idx++; renderSlide(); }

async function initGenerate(){
  document.getElementById('lockEval').onclick = async ()=>{
    await fetch('/api/diagnosis/evaluate',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({force:false})});
    alert('Evaluation locked');
  };
  document.getElementById('lockFlavor').onclick = async ()=>{
    await fetch('/api/flavor/lock',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({force:false})});
    alert('Flavor locked');
  };
  document.getElementById('compileAnalysis').onclick = async ()=>{
    await fetch('/api/analysis/compile',{method:'POST'});
    alert('Analysis compiled');
  };
  document.getElementById('genBtn').onclick = async ()=>{
    const res = await fetch('/api/recipes/generate',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({count:3, meals:["lunch","dinner","snack"]})});
    const recipes = await res.json();
    document.getElementById('out').textContent = JSON.stringify(recipes,null,2);
    // optional: window.location.href = '/recipe/index.html';
  };
}