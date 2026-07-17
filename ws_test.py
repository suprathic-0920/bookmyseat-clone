import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect("ws://127.0.0.1:8000/ws/theater/1/seats/") as ws:
            print("Connected!")
            await ws.send(json.dumps({'action': 'hold', 'seat_id': '5'}))
            res = await ws.recv()
            print("Received:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
