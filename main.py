from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import time
import os
import json
from datetime import datetime
import uvicorn

# process start time for a small uptime value
_START_TIME = time.time()

app = FastAPI(title="AI Compliance Admin - Stealth UI")


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Serve a single-file stealth black admin dashboard HTML page.

    Everything (CSS, JS, and sample metrics) is embedded directly in the
    returned HTML string so no external files or FileResponse are used.
    """

    # Server-side sample metrics
    net_worth = 1_000_000_000_000  # $1 trillion
    profits = 250_000_000
    losses = 0
    compliance_risk = 0.0
    uptime_seconds = int(time.time() - _START_TIME)
    generated_at = datetime.utcnow().isoformat() + "Z"
    hostname = os.getenv("HOSTNAME", "localhost")

    metrics = {
        "net_worth": net_worth,
        "profits": profits,
        "losses": losses,
        "compliance_risk": compliance_risk,
        "uptime_seconds": uptime_seconds,
        "generated_at": generated_at,
        "host": hostname,
    }

    metrics_json = json.dumps(metrics)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Stealth Admin Dashboard</title>
  <style>
    /* Stealth black theme */
    :root {
      --bg: #070707;
      --panel: #0f0f0f;
      --muted: #6b6b6b;
      --accent: #00e6a8;
      --glass: rgba(255,255,255,0.02);
      --glass-2: rgba(255,255,255,0.03);
      --card-radius: 12px;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Segoe UI Mono", "Helvetica Neue", monospace;
    }

    html,body{height:100%;margin:0;font-family:Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; background:linear-gradient(180deg,#050505 0%, #0a0a0a 100%);color:#e9e9e9}

    .container{max-width:1200px;margin:36px auto;padding:28px}

    .panel{background:var(--panel);border-radius:var(--card-radius);box-shadow:0 6px 30px rgba(0,0,0,0.6);padding:28px}

    .header{display:flex;align-items:center;justify-content:space-between;gap:20px}

    /* Cursive greeting banner */
    .greeting{
      font-family: 'Brush Script MT', 'Pacifico', cursive; /* cursive fallback */
      font-size:44px;color:var(--accent);letter-spacing:1px;margin:0;padding:8px 14px;background:linear-gradient(90deg, rgba(0,230,168,0.08), rgba(0,230,168,0.03));border-radius:10px}

    .sub{color:var(--muted);font-size:14px}

    .metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin-top:22px}

    .metric{background:var(--glass);padding:18px;border-radius:12px;border:1px solid var(--glass-2);min-height:96px}
    .metric h3{margin:0;font-size:14px;color:var(--muted)}
    .metric .value{font-family:var(--mono);font-size:22px;margin-top:8px}

    .big{grid-column:span 2;padding:28px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start}

    .net-worth{font-size:34px;font-weight:700;color:#fff}

    .footer{margin-top:18px;color:var(--muted);font-size:13px}

    /* small responsive */
    @media (max-width:520px){.metrics{grid-template-columns:1fr}.greeting{font-size:28px}}

    /* subtle hover */
    .metric:hover{transform:translateY(-4px);transition:transform 180ms ease}

    /* tiny helper */
    .muted{color:var(--muted);font-size:12px}
  </style>
</head>
<body>
  <div class="container">
    <div class="panel">
      <div class="header">
        <div>
          <div class="greeting">Welcome, Operator</div>
          <div class="sub">Stealth Admin Dashboard</div>
        </div>
        <div class="muted">Generated at: {generated_at}</div>
      </div>

      <div class="metrics">
        <div class="metric big">
          <div class="net-worth">Net Worth</div>
          <div id="netWorth" style="font-size:36px;font-weight:800;margin-top:8px;color:var(--accent);">$0</div>
          <div class="muted" style="margin-top:8px">Monitored assets and liabilities</div>
        </div>

        <div class="metric">
          <h3>Profits</h3>
          <div class="value" id="profits">$0</div>
          <div class="muted">YTD gains</div>
        </div>

        <div class="metric">
          <h3>Losses</h3>
          <div class="value" id="losses">$0</div>
          <div class="muted">YTD losses</div>
        </div>

        <div class="metric">
          <h3>Compliance Risk</h3>
          <div class="value" id="risk">0%</div>
          <div class="muted">Estimated regulatory exposure</div>
        </div>

        <div class="metric">
          <h3>Server Uptime</h3>
          <div class="value" id="uptime">0s</div>
          <div class="muted">Since process start</div>
        </div>

        <div class="metric">
          <h3>Environment</h3>
          <div class="value">{hostname}</div>
          <div class="muted">Host process</div>
        </div>

      </div>

      <div class="footer">Tip: This panel is self-contained and served directly from the FastAPI process. No external assets are loaded.</div>
    </div>
  </div>

  <script>
    // Server-side metrics embedded as JSON
    const SERVER_METRICS = {metrics_json};

    // Animate a numeric counter (handles large values smoothly)
    function animateCount(el, start, end, duration){
      const startTime = performance.now();
      function tick(now){
        const elapsed = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - elapsed, 3); // ease out
        const current = Math.floor(start + (end - start) * eased);
        el.textContent = "$" + current.toLocaleString();
        if(elapsed < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    }

    function formatCurrency(n){
      return "$" + n.toLocaleString();
    }

    function formatUptime(s){
      s = Number(s);
      const h = Math.floor(s/3600); s %= 3600;
      const m = Math.floor(s/60); const sec = s % 60;
      let out = "";
      if(h>0) out += h + "h ";
      if(m>0) out += m + "m ";
      out += sec + "s";
      return out;
    }

    document.addEventListener('DOMContentLoaded', function(){
      const netEl = document.getElementById('netWorth');
      const pEl = document.getElementById('profits');
      const lEl = document.getElementById('losses');
      const rEl = document.getElementById('risk');
      const uEl = document.getElementById('uptime');

      // Animate net worth over 3s
      animateCount(netEl, 0, SERVER_METRICS.net_worth, 3000);

      pEl.textContent = formatCurrency(SERVER_METRICS.profits);
      lEl.textContent = formatCurrency(SERVER_METRICS.losses);
      rEl.textContent = (Number(SERVER_METRICS.compliance_risk)).toFixed(1) + "%";
      uEl.textContent = formatUptime(SERVER_METRICS.uptime_seconds);
    });
  </script>
</body>
</html>
"""

    return HTMLResponse(content=html, status_code=200)


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    uvicorn.run(app, host='0.0.0.0', port=port)
