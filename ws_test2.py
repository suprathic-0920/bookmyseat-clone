import asyncio
import websockets
import json

async def test():
    try:
        async with websockets.connect("ws://127.0.0.1:8000/ws/theater/1/seats/") as ws1:
            async with websockets.connect("ws://127.0.0.1:8000/ws/theater/1/seats/") as ws2:
                print("Both Connected!")
                await ws1.send(json.dumps({'action': 'hold', 'seat_id': '10'}))
                
                res1 = await ws1.recv()
                print("WS1 Received:", res1)
                
                res2 = await ws2.recv()
                print("WS2 Received:", res2)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
