"""Minimal local dashboard (docs/17 Phase 10 stable local UI).

A single self-contained HTML page served at the root. It talks only to the
documented local API — no build tooling, no external assets — which keeps
candidate data on the local machine (docs/01 Local First).
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Platform</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; margin: 0; padding: 1.5rem;
         max-width: 1100px; margin-inline: auto; line-height: 1.4; }
  h1 { font-size: 1.4rem; } h2 { font-size: 1.1rem; margin-top: 1.75rem; }
  .card { border: 1px solid #8884; border-radius: 8px; padding: 0.75rem 1rem;
          margin: 0.5rem 0; }
  .row { display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap; }
  .grow { flex: 1; min-width: 12rem; }
  .status { font-size: 0.8rem; padding: 0.1rem 0.5rem; border-radius: 999px;
            border: 1px solid #8886; }
  button { cursor: pointer; border-radius: 6px; border: 1px solid #8886;
           padding: 0.3rem 0.7rem; background: #4477dd; color: white; }
  button.secondary { background: transparent; color: inherit; }
  button:disabled { opacity: 0.4; cursor: default; }
  table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
  th, td { text-align: left; padding: 0.3rem 0.5rem; border-bottom: 1px solid #8883; }
  .muted { color: #8888; font-size: 0.8rem; }
  .attn { color: #cc6600; font-size: 0.8rem; }
  #toast { position: fixed; bottom: 1rem; right: 1rem; background: #222;
           color: #fff; padding: 0.6rem 1rem; border-radius: 8px; display: none; }
  .skip { position: absolute; left: -999px; }
  .skip:focus { position: static; display: inline-block; margin-bottom: .5rem; }
  .degraded { color: #cc3300; font-weight: 600; }
  button:focus-visible { outline: 3px solid #4477dd; outline-offset: 2px; }
</style>
</head>
<body>
<a href="#applications-section" class="skip">Skip to applications</a>
<h1>Job Platform <span id="version" class="muted"></span></h1>
<p id="health" class="muted" role="status" aria-live="polite">Loading…</p>
<p id="candidate" class="muted">Loading…</p>

<main>
<section id="applications-section" aria-labelledby="apps-heading">
<h2 id="apps-heading">Applications
  <button class="secondary" onclick="load()" aria-label="Refresh applications">Refresh</button></h2>
<div id="applications"></div>
</section>

<section aria-labelledby="queues-heading">
<h2 id="queues-heading">Queues</h2>
<div id="queues"></div>
</section>

<section aria-labelledby="history-heading">
<h2 id="history-heading">History
  <button class="secondary" onclick="exportXlsx()">Export XLSX</button></h2>
<div id="history"></div>
</section>
</main>

<div id="toast" role="alert" aria-live="assertive"></div>

<script>
const api = (p, opts) => fetch(p, opts).then(async r => {
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error((body.error && body.error.message) || r.statusText);
  return body;
});
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.style.display = 'block';
  setTimeout(() => { t.style.display = 'none'; }, 4000);
}
async function act(fn) {
  try { await fn(); await load(); } catch (e) { toast('Error: ' + e.message); }
}

async function load() {
  const health = await api('/api/health');
  document.getElementById('version').textContent = 'v' + health.version +
    ' · provider: ' + health.provider;

  const sys = await api('/api/system/health');
  const el = document.getElementById('health');
  if (sys.healthy) {
    el.textContent = 'System healthy — ' +
      sys.components.map(c => c.name + ': ' + c.state).join(' · ');
    el.className = 'muted';
  } else {
    const bad = sys.components.filter(c => c.state !== 'ok' && c.state !== 'not_applicable');
    el.textContent = 'Degraded components: ' +
      bad.map(c => c.name + ' (' + c.detail + ')').join(', ');
    el.className = 'degraded';
  }

  const cand = await api('/api/candidate/status');
  document.getElementById('candidate').textContent = cand.ok
    ? `Candidate ready — ${cand.resumes.length} resume(s), ${cand.warnings.length} warning(s)`
    : `Candidate has ${cand.errors.length} error(s)`;

  const apps = await api('/api/applications');
  document.getElementById('applications').innerHTML = apps.applications.length
    ? apps.applications.map(appCard).join('')
    : '<p class="muted">No application packages yet.</p>';

  const queues = await api('/api/queue');
  document.getElementById('queues').innerHTML = queues.queues.length
    ? queues.queues.map(queueCard).join('')
    : '<p class="muted">No queues yet.</p>';

  const hist = await api('/api/history');
  document.getElementById('history').innerHTML = hist.applications.length
    ? historyTable(hist.applications)
    : '<p class="muted">No submitted applications yet.</p>';
}

function appCard(a) {
  const id = a.package_id;
  const attn = (a.attention_items || []).filter(i => i.blocking)
    .map(i => `<div class="attn">⚠ ${i.message}</div>`).join('');
  const actions = [
    `<button class="secondary" onclick="act(()=>api('/api/applications/${id}/review',{method:'POST'}))">Review</button>`,
    `<button class="secondary" onclick="act(()=>api('/api/applications/${id}/readiness',{method:'POST'}))">Readiness</button>`,
    `<button class="secondary" onclick="act(()=>api('/api/queue',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({package_ids:['${id}']})}))">Queue</button>`,
    `<button onclick="act(()=>api('/api/applications/${id}/approve',{method:'POST',headers:{'content-type':'application/json'},body:'{}'}))">Approve</button>`,
    `<button onclick="submitApp('${id}')">Submit</button>`,
  ].join(' ');
  return `<div class="card"><div class="row">
    <span class="grow"><strong>${a.title}</strong> — ${a.company}</span>
    <span class="status">${a.status}</span></div>
    <div class="muted">${id} · resume: ${a.selected_resume || 'none'} ·
      cover letter: ${a.cover_letter ? 'yes' : 'no'}</div>
    ${attn}<div class="row" style="margin-top:.5rem">${actions}</div></div>`;
}

async function submitApp(id) {
  if (!confirm('Submit this application? This performs the final click.')) return;
  await act(async () => {
    const r = await api('/api/applications/' + id + '/submit', {method:'POST'});
    toast('Submission ' + r.status);
  });
}

function queueCard(q) {
  const items = q.items.map(i =>
    `<tr><td>${i.position}</td><td>${i.package_id}</td>
     <td>${i.status}</td><td class="muted">${i.error || ''}</td></tr>`).join('');
  const runnable = q.status === 'ready' || q.status === 'paused';
  return `<div class="card"><div class="row">
    <span class="grow"><strong>${q.queue_id}</strong></span>
    <span class="status">${q.status}</span>
    <button onclick="act(()=>api('/api/queue/${q.queue_id}/run',{method:'POST'}))"
      ${runnable ? '' : 'disabled'}>Run</button>
    <button class="secondary" onclick="act(()=>api('/api/queue/${q.queue_id}/pause',{method:'POST'}))">Pause</button>
    </div><table><tr><th>#</th><th>Package</th><th>Status</th><th></th></tr>
    ${items}</table></div>`;
}

function historyTable(rows) {
  return `<table><tr><th>Company</th><th>Title</th><th>Applied</th>
    <th>Status</th><th>Notes</th></tr>` + rows.map(r =>
    `<tr><td>${r.company}</td><td>${r.job_title}</td><td>${r.date_applied}</td>
     <td>${r.status}</td><td class="muted">${r.notes}</td></tr>`).join('') + '</table>';
}

async function exportXlsx() {
  try { const r = await api('/api/history/export'); toast('Wrote ' + r.path); }
  catch (e) { toast('Error: ' + e.message); }
}

load().catch(e => toast('Error: ' + e.message));
</script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def dashboard() -> str:
    return _PAGE
