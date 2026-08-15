from datetime import date, datetime
import time
import os
import shutil
from typing import List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="AI Compliance Admin Dashboard")

# Record process start time for a simple uptime metric
_START_TIME = time.time()


class Contract(BaseModel):
    id: str
    name: str
    start_date: date
    value: int  # in cents (or smallest currency unit) for precision
    status: str


class ServerHealth(BaseModel):
    status: str
    uptime_seconds: int
    disk_total_bytes: int
    disk_used_bytes: int
    disk_free_bytes: int
    load_average: List[float] | None


class Dashboard(BaseModel):
    net_worth: int
    profits: int
    losses: int
    server_health: ServerHealth
    active_company_contracts: List[Contract]
    compliance_risk_percent: float
    generated_at: datetime


def _get_server_health() -> ServerHealth:
    # uptime
    uptime_seconds = int(time.time() - _START_TIME)

    # disk usage (safe fallback if root not available)
    try:
        root_path = os.getenv("ROOT_PATH", "/")
        du = shutil.disk_usage(root_path)
        disk_total = du.total
        disk_used = du.used
        disk_free = du.free
    except Exception:
        # Fallback to zeros if disk usage can't be determined
        disk_total = disk_used = disk_free = 0

    # load average (may not be available on Windows)
    try:
        loadavg = list(os.getloadavg())
    except Exception:
        loadavg = None

    return ServerHealth(
        status="healthy",
        uptime_seconds=uptime_seconds,
        disk_total_bytes=disk_total,
        disk_used_bytes=disk_used,
        disk_free_bytes=disk_free,
        load_average=loadavg,
    )


@app.get("/admin/dashboard", response_model=Dashboard)
def admin_dashboard() -> Dashboard:
    """Return master metrics for the admin dashboard.

    This endpoint intentionally returns mock/sample values (including the
    user's requested figures) so it is deterministic and won't raise runtime
    errors when called.
    """

    # Business metrics (the values requested)
    net_worth = 1_000_000_000_000  # 1 trillion
    profits = 250_000_000
    losses = 0

    # sample active contracts
    contracts = [
        Contract(
            id="C-0001",
            name="Global Supply Agreement",
            start_date=date(2024, 1, 1),
            value=5_000_000_00,  # example in cents
            status="active",
        ),
        Contract(
            id="C-0002",
            name="Cloud Services Contract",
            start_date=date(2025, 6, 15),
            value=12_500_000_00,
            status="active",
        ),
    ]

    dashboard = Dashboard(
        net_worth=net_worth,
        profits=profits,
        losses=losses,
        server_health=_get_server_health(),
        active_company_contracts=contracts,
        compliance_risk_percent=0.0,  # 0% risk as requested
        generated_at=datetime.utcnow(),
    )

    return dashboard


if __name__ == "__main__":
    # uvicorn runner at the bottom as requested
    # Use a fixed port (8000) by default. To change port, set the PORT env var.
    port = int(os.getenv("PORT", "8000"))
    # Run the app. Importing uvicorn at top ensures the symbol exists.
    uvicorn.run(app, host="0.0.0.0", port=port)
