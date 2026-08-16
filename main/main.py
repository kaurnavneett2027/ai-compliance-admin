from datetime import datetime
import json
import os
import time
from typing import Dict

from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# AI Compliance Admin - Hypercar Cockpit Styled Dashboard
# This main.py writes a static HTML dashboard file at startup and serves it
# with FileResponse on the root path. It also exposes an API to read and
# simulate metrics: total_files_checked, simulated ARR, and core engine velocity.

app = FastAPI(title="AI Compliance Admin - Hypercar Cockpit")

# where we store the generated HTML and persistent state
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
HTML_PATH = os.path.join(STATIC_DIR, "dashboard.html")
STATE_PATH = os.path.join(STATIC_DIR, "state.json")

# process start time for velocity & uptime
_START_TIME = time.time()

# default simulation constants
ARR_PER_FILE_USD = 120.0  # simulated ARR contribution per file checked (USD)

# ensure static dir exists
os.makedirs(STATIC_DIR, exist_ok=True)


class Metrics(BaseModel):
    total_files_checked: int
    simulated_arr_usd: float
    engine_velocity_files_per_min: float
    uptime_seconds: int
    generated_at: datetime


def _load_state() -> Dict:
    if not os.path.exists(STATE_PATH):
        return {"total_files_checked": 0}
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"total_files_checked": 0}


def _save_state(state: Dict) -> None:
    try:
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        # best-effort - if disk fails, we still run in-memory
        pass


def _current_metrics() -> Metrics:
    state = _load_state()
    total = int(state.get("total_files_checked", 0))
    uptime = int(time.time() - _START_TIME)
    # engine velocity: files processed per minute (simulated as average over uptime)
    engine_velocity = (total / uptime * 60.0) if uptime > 0 else 0.0
    simulated_arr = total * ARR_PER_FILE_USD

    return Metrics(
        total_files_checked=total,
        simulated_arr_usd=round(simulated_arr, 2),
        engine_velocity_files_per_min=round(engine_velocity, 2),
        uptime_seconds=uptime,
        generated_at=datetime.utcnow(),
    )


# Write the hypercar-cockpit-styled HTML to disk (overwrites each start)
DASHBOARD_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>AI Compliance Admin - Hypercar Cockpit</title>
  <style>
    /* Hypercar cockpit styling: dark, neon accents, layered glass, digital readouts */
    :root{
      --bg:#050608;
      --glass:rgba(255,255,255,0.03);
      --accent:#00fff6;
      --accent-2:#ff3d81;
      --muted:#9aa3b2;
      --panel:#0a0c0f;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }
    html,body{height:100%;margin:0;background:linear-gradient(180deg,#030306 0%, #071018 60%);color:#e6f7ff}
    .wrap{display:flex;flex-direction:column;height:100%;padding:28px;gap:18px}
    header{display:flex;align-items:center;gap:20px}
    .logo{width:84px;height:56px;border-radius:10px;background:linear-gradient(135deg,var(--accent),var(--accent-2));box-shadow:0 6px 30px rgba(0,255,246,0.06), inset 0 -4px 20px rgba(255,61,129,0.04);display:flex;align-items:center;justify-content:center;font-weight:700;color:#031;letter-spacing:1px}
    h1{font-size:20px;margin:0}
    .subtitle{color:var(--muted);font-size:13px}
    main{display:flex;gap:18px;flex:1}

    .panel{background:var(--panel);border-radius:12px;padding:18px;box-shadow:0 4px 40px rgba(0,0,0,0.6);flex:1;backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,0.03)}
    .panel.right{width:420px;min-width:300px}

    .gauges{display:flex;gap:12px}
    .gauge{flex:1;background:linear-gradient(180deg,rgba(255,255,255,0.02),transparent);padding:14px;border-radius:10px;display:flex;flex-direction:column;align-items:center}

    .big-number{font-size:36px;font-weight:700;color:var(--accent)}
    .small{color:var(--muted);font-size:12px}

    .strip{display:flex;gap:12px;margin-top:12px}
    .strip .card{flex:1;padding:12px;border-radius:8px;background:var(--glass);border:1px solid rgba(255,255,255,0.02)}

    /* circular gauge */
    .arc{width:128px;height:128px}
    svg text{font-family:inherit}

    footer{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:12px}

    /* neon ticks and labels */
    .metric-label{font-size:13px;color:var(--muted)}
    .metric-value{font-size:22px;font-weight:700;color:#fff}

    button.cta{background:linear-gradient(90deg,var(--accent),var(--accent-2));color:#041;border:none;padding:10px 14px;border-radius:8px;font-weight:700;cursor:pointer}

    /* responsive */
    @media (max-width:860px){main{flex-direction:column}.panel.right{width:auto}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div class="logo">AIC</div>
      <div>
        <h1>AI Compliance — Admin Cockpit</h1>
        <div class="subtitle">Hypercar diagnostics for compliance, ARR & core engine velocity</div>
      </div>
    </header>
    <main>
      <section class="panel left">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <div class="metric-label">Total files checked</div>
            <div id="files" class="big-number">0</div>
            <div class="small">Live counter — represents files validated by the core engine</div>
          </div>
          <div>
            <div class="metric-label">Simulated ARR (USD)</div>
            <div id="arr" class="big-number" style="color:var(--accent-2)">$0.00</div>
            <div class="small">ARR calculated as files × $120/year</div>
          </div>
        </div>

        <div class="strip" style="margin-top:18px">
          <div class="card">
            <div class="metric-label">Core engine velocity</div>
            <div id="velocity" class="metric-value">0 files/min</div>
            <div class="small">Average throughput since app start</div>
          </div>
          <div class="card">
            <div class="metric-label">Uptime</div>
            <div id="uptime" class="metric-value">0s</div>
            <div class="small">Process uptime</div>
          </div>
        </div>

        <div style="margin-top:18px">
          <div class="metric-label">Live Gauges</div>
          <div class="gauges" style="margin-top:8px">
            <div class="gauge">
              <svg class="arc" viewBox="0 0 120 120" id="gauge1">
                <defs>
                  <linearGradient id="g1" x1="0" x2="1">
                    <stop offset="0%" stop-color="#00fff6"/>
                    <stop offset="100%" stop-color="#ff3d81"/>
                  </linearGradient>
                </defs>
                <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="12"/>
                <path id="arcPath" d="" stroke="url(#g1)" stroke-width="12" fill="none" stroke-linecap="round"/>
                <text x="60" y="66" font-size="14" text-anchor="middle" fill="#fff">0%</text>
              </svg>
              <div class="small" style="margin-top:8px">Compliance risk</div>
            </div>
            <div class="gauge">
              <svg class="arc" viewBox="0 0 120 120" id="gauge2">
                <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="12"/>
                <path id="arcPath2" d="" stroke="#00fff6" stroke-width="12" fill="none" stroke-linecap="round"/>
                <text x="60" y="66" font-size="14" text-anchor="middle" fill="#fff">0</text>
              </svg>
              <div class="small" style="margin-top:8px">Files / session</div>
            </div>
          </div>
        </div>

      </section>

      <aside class="panel right">
        <div style="display:flex;align-items:center;justify-content:space-between">
          <div>
            <div class="metric-label">Engine Controls</div>
            <div class="small">Manual simulation controls for testing</div>
          </div>
          <div>
            <button class="cta" onclick="simulate(10)">Check +10 files</button>
          </div>
        </div>

        <div style="margin-top:18px">
          <div class="metric-label">Quick actions</div>
          <div style="margin-top:8px;display:flex;gap:8px">
            <button style="background:#061222;color:#fff;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);cursor:pointer" onclick="simulate(1)">+1 file</button>
            <button style="background:#061222;color:#fff;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.03);cursor:pointer" onclick="simulate(100)">+100 files</button>
          </div>
        </div>

        <div style="margin-top:20px">
          <div class="metric-label">Diagnostics</div>
          <pre id="diag" style="background:rgba(255,255,255,0.02);padding:12px;border-radius:8px;color:var(--muted);font-size:12px">initializing...</pre>
        </div>
      </aside>
    </main>

    <footer>
      <div>AI Compliance Admin • Hypercar Cockpit</div>
      <div id="ts">--</div>
    </footer>
  </div>

<script>
async function fetchMetrics(){
  try{
    const res = await fetch('/api/metrics');
    const json = await res.json();
    document.getElementById('files').textContent = new Intl.NumberFormat().format(json.total_files_checked);
    document.getElementById('arr').textContent = '$' + new Intl.NumberFormat().format(json.simulated_arr_usd.toFixed(2));
    document.getElementById('velocity').textContent = json.engine_velocity_files_per_min + ' files/min';
    document.getElementById('uptime').textContent = formatUptime(json.uptime_seconds);
    document.getElementById('ts').textContent = 'Updated: ' + new Date(json.generated_at).toLocaleTimeString();

    // update gauges (simple percent for compliance risk simulated by modulo)
    const p = Math.min(100, Math.floor((json.total_files_checked % 500) / 5));
    setArc('#gauge1 path', p);
    setArc2('#gauge2 path', Math.min(100, Math.floor(json.engine_velocity_files_per_min)));

    document.getElementById('diag').textContent = JSON.stringify(json, null, 2);
  }catch(e){
    console.error(e);
  }
}

function setArc(selector, percent){
  const svg = document.querySelector(selector);
  if(!svg) return;
  const r = 48;
  const c = 2 * Math.PI * r;
  const value = Math.max(0, Math.min(100, percent));
  const dash = c * (value/100);
  svg.setAttribute('d', describeArc(60,60,r, -90, -90 + (value/100)*180));
}
function setArc2(selector, percent){
  // full semicircle scale 0-100
  setArc(selector, percent);
}

// draw a semicircular arc path (approximate)
function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
  var angleInRadians = (angleInDegrees-90) * Math.PI / 180.0;
  return {
    x: centerX + (radius * Math.cos(angleInRadians)),
    y: centerY + (radius * Math.sin(angleInRadians))
  };
}
function describeArc(x, y, radius, startAngle, endAngle){
  var start = polarToCartesian(x, y, radius, endAngle);
  var end = polarToCartesian(x, y, radius, startAngle);
  var largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  var d = [
    "M", start.x, start.y,
    "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y
  ].join(' ');
  return d;
}

function formatUptime(s){
  if(s<60) return s + 's';
  const m = Math.floor(s/60);
  if(m<60) return m + 'm ' + (s%60) + 's';
  const h = Math.floor(m/60);
  return h + 'h ' + (m%60) + 'm';
}

async function simulate(n){
  try{
    await fetch('/api/check', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({count:n})});
    await fetchMetrics();
  }catch(e){console.error(e)}
}

// poll
setInterval(fetchMetrics, 1200);
fetchMetrics();
</script>
</body>
</html>
"""

# write the HTML file
try:
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(DASHBOARD_HTML)
except Exception:
    # if writing fails, we still continue; FileResponse may fail at runtime
    pass


@app.get("/", response_class=FileResponse)
def root():
    """Serve the static hypercar cockpit dashboard HTML using FileResponse."""
    # FileResponse requires a filesystem path. We wrote the file at startup.
    return FileResponse(HTML_PATH, media_type="text/html")


@app.get("/api/metrics")
def metrics():
    """Return the current simulated metrics as JSON."""
    m = _current_metrics()
    return JSONResponse(content=m.dict())


@app.post("/api/check")
def check_files(payload: Dict = Body(...)):
    """Simulate checking `count` files. Body: {"count": <int>}"""
    try:
        count = int(payload.get("count", 0))
    except Exception:
        count = 0
    if count <= 0:
        return JSONResponse(status_code=400, content={"error": "count must be a positive integer"})

    state = _load_state()
    total = int(state.get("total_files_checked", 0)) + count
    state["total_files_checked"] = total
    _save_state(state)
    return JSONResponse(content=_current_metrics().dict())


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
