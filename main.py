import asyncio
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from snmp_manager import *
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

monitoring_manager = MonitoringManager(["192.168.1.1"], 1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    poll_task = asyncio.create_task(monitoring_manager.snmp_poll())
    yield
    poll_task.cancel()
    await poll_task

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", context={"result" : monitoring_manager.monitoring_result})

@app.get("/get/metrics", response_class=HTMLResponse)
def get_metrics(request: Request):
    if not monitoring_manager.monitoring_result:
        return "<p>N/A</p>"
    else:
        string = []

        for ip, data in monitoring_manager.monitoring_result.items():
            string.append(f"<p>IP: {ip}</p>")
            string.append(f"<p>Uptime: {data['uptime']}</p>")

        return ''.join(string)