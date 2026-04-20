import asyncio
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from snmp_manager import *
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

monitoring_manager = MonitoringManager(["192.168.1.1"], 1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем фоновую задачу опроса
    poll_task = asyncio.create_task(monitoring_manager.snmp_poll())
    yield
    # При выключении сервера – останавливаем задачу
    poll_task.cancel()
    await poll_task

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", context={"monitoring_result" : monitoring_manager.monitoring_result})
