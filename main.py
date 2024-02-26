"""
Simple python server accepting
1. APIs
2. Websocket connections
3. Socketio connections

We are using fastapi framework for building the server
and python-socketio for creating socketio connections on top of uvicorn app
https://fastapi.tiangolo.com/#requirements
"""

from fastapi import FastAPI, WebSocket
from socketio import AsyncServer, ASGIApp

# fastapi object
app = FastAPI()

# create an ASGI application middleware for Socket.IO.
sio = AsyncServer(async_mode='asgi', cors_allowed_origins='*')
sio_asgi_app = ASGIApp(sio, app)

# mounting to main application who receives traffic to route all connections form this endpoint to socketio instance
app.mount("/socket.io", sio_asgi_app)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    print(request.base_url, request.client.host)
    try:
        response: Response = await call_next(request)
    finally:
        print(response.status_code,)
    return response

@app.get("/hello")
def return_hello():
    return "hello world!"
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            print('waiting for messge', websocket.application_state)
            data = await websocket.receive()
            await websocket.send_text(f"Message text was: {data}")
        except:
            break
    
    print("Disconnected!!!")

@sio.on('connect', namespace="/tring")
def connect_handler(sid, environ):
    print(sid)
    print('Connection request')


if __name__ == '__main__':
    import uvicorn

    # run the application as uvicorn server
    uvicorn.run("main:app", host='0.0.0.0', port=8000)
