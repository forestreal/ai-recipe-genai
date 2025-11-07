async function fetchRecipes() {
  const res = await fetch('/api/recipes/generate', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({count:3, meals:["lunch","dinner","snack"]})
  });
  return await res.json();
}
function render(list) {
  const root = document.getElementById('recipeList');
  root.innerHTML = '';
  list.forEach(r => {
    const card = document.createElement('div');
    card.className = 'recipe-card';
    card.innerHTML = `<h2>${r.title}</h2>
      <div><b>${r.cuisine}</b> • ${r.meal_type} • ${r.prep_time} • ${r.difficulty}</div>
      <pre>${JSON.stringify(r, null, 2)}</pre>`;
    root.appendChild(card);
  });
}
document.getElementById('regenBtn').onclick = async () => render(await fetchRecipes());
window.addEventListener('DOMContentLoaded', async () => render(await fetchRecipes()));