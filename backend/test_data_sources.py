import httpx
import asyncio

async def test_polymarket():
    print("Testing Polymarket API...")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
            # Test clob API
            r = await c.get('https://clob.polymarket.com/markets')
            print(f"clob.polymarket.com Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Markets count: {len(data)}")
                if data:
                    print(f"First market: {list(data[0].keys())[:10]}")
            else:
                print(f"Response: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Test gamma API (alternative)
    print("Testing Polymarket Gamma API...")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
            r = await c.get('https://gamma-api.polymarket.com/markets', params={
                'limit': 10,
                'closed': 'false'
            })
            print(f"gamma-api Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Markets count: {len(data)}")
                if data:
                    print(f"First market keys: {list(data[0].keys())[:15]}")
                    print(f"Question: {data[0].get('question', 'N/A')[:80]}")
            else:
                print(f"Response: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

async def test_kalshi():
    print()
    print("Testing Kalshi API...")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
            r = await c.get('https://trading-api.kalshi.com/trade-api/v2/markets', params={
                'limit': 10,
                'status': 'open'
            })
            print(f"Kalshi Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                markets = data.get('markets', [])
                print(f"Markets count: {len(markets)}")
                if markets:
                    print(f"First market: {markets[0].get('title', markets[0].get('event_ticker', 'N/A'))[:80]}")
            else:
                print(f"Response: {r.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_polymarket())
asyncio.run(test_kalshi())
