import asyncio
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from snmp_manager import *
from device_manager import *
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, Response
from datetime import datetime


def convert_uptime(seconds: int) -> str:
    return datetime.fromtimestamp(seconds).strftime('%d days, %H:%M:%S')


device_manager = DeviceManager()
monitoring_manager = MonitoringManager()


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
    return templates.TemplateResponse(request, "index.html",
                                      context={
                                          "monitoring_manager": monitoring_manager
                                      })


@app.get("/get/metrics", response_class=HTMLResponse)
def get_metrics(request: Request):
    if not monitoring_manager.monitoring_result:
        return "<p>N/A</p>"
    else:
        string = [f"""
            <table>
                <thead>
                    <tr>
                        <th>IP</th> <th>CPU</th> <th>RAM</th> <th>Uptime</th>
                    </tr>
                </thead>
                <tbody>
        """]

        for ip, data in monitoring_manager.monitoring_result.items():
            string.append(f"""
                        <tr>
                            <td>{ip}<br/>{data['name']}</td> <td>--</td> <td>--</td> <td>{convert_uptime(int(data['uptime']) // 100)}</td>
                        </tr>
            """)

        string.append("</tbody> </table>")
        return ''.join(string)


@app.post("/post/interval", response_class=HTMLResponse)
def post_interval(request: Request, interval: int = Form(...)):
    try:
        monitoring_manager.interval = interval
    except ValueError:
        message = "Недопустимое значение интервала"

    message = f"Интервал опроса изменён: {interval} сек."
    return templates.TemplateResponse(request, "panel.html",
                                      context={
                                          "monitoring_manager": monitoring_manager,
                                          "message": message
                                      })


@app.get("/get/device-list", response_class=HTMLResponse)
def get_device_list(request: Request):
    if (device_manager.device_list is None) or (len(device_manager.device_list) == 0):
        return "<p>Список устройств пуст</p>"
    else:
        return_string = ["<ul id='device-list'>"]
        for device in device_manager.device_list:
            return_string.append(
                f'<li class="device-list-element" hx-post="/post/delete-device/{device["id"]}" hx-target="#device-list-div" hx-swap="innerHTML" hx-trigger="click">' +
                device["ip"] + "</li>")
        return_string.append("</ul>")
        return "".join(return_string)


@app.post("/post/new-device", response_class=HTMLResponse)
def post_new_device(request: Request, device_address: str = Form(...)):
    # append device list
    device_manager.add_device(device_address)
    monitoring_manager.append_ip_list(device_address)

    # return updated list
    return get_device_list(request)


@app.post("/post/delete-device/{removing_id}", response_class=HTMLResponse)
def post_delete_device(request: Request, removing_id: int):
    device_manager.delete_device(removing_id)
    return get_device_list(request)
