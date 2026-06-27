import urllib.request
import json
import random

base = 'http://localhost:8002/api'

def test_api(name, endpoint, method='GET', data=None, token=None):
    try:
        headers = {}
        if data:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data).encode()
        else:
            body = None
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        req = urllib.request.Request(
            f'{base}{endpoint}',
            data=body,
            headers=headers,
            method=method
        )
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        return True, resp.status, result
    except Exception as e:
        return False, str(e), None

print('=== 新功能API测试 ===')
print()

# 1. 系统配置API
ok, status, body = test_api('config', '/config')
if ok:
    wallet = body.get('usdt_wallet', 'N/A')
    tiers = list(body.get('subscription_tiers', {}).keys())
    print(f'1. 系统配置API: PASS')
    print(f'   USDT钱包: {wallet[:25]}...')
    print(f'   订阅等级: {tiers}')
else:
    print(f'1. 系统配置API: FAIL - {status}')

print()

# 2. 注册测试用户
username = f'qa_user_{random.randint(10000, 99999)}'
ok, status, body = test_api('register', '/auth/register', 'POST', {
    'username': username,
    'password': 'test123456',
    'email': f'{username}@test.com'
})
if ok:
    token = body.get('access_token', '')
    print(f'2. 注册测试用户: PASS - {username}')
else:
    token = ''
    print(f'2. 注册测试用户: FAIL - {status}')

print()

# 3. 创建订单
order_id = ''
if token:
    ok, status, body = test_api('create_order', '/subscription/create-order', 'POST', {
        'tier': 'pro',
        'payment_method': 'usdt'
    }, token)
    if ok:
        order_id = body.get('order_id', '')
        wallet = body.get('wallet_address', '')
        print(f'3. 创建订单API: PASS')
        print(f'   订单号: {order_id}')
        print(f'   钱包地址: {wallet[:25]}...')
    else:
        print(f'3. 创建订单API: FAIL - {status}')
else:
    print(f'3. 创建订单API: SKIP')

print()

# 4. 查询订单状态
if token and order_id:
    ok, status, body = test_api('order_status', f'/orders/{order_id}', 'GET', None, token)
    if ok:
        print(f'4. 查询订单状态: PASS')
        print(f'   状态: {body.get("status")}')
        print(f'   等级: {body.get("tier_name")}')
    else:
        print(f'4. 查询订单状态: FAIL - {status}')
else:
    print(f'4. 查询订单状态: SKIP')

print()

# 5. 我的订单
if token:
    ok, status, body = test_api('my_orders', '/my/orders', 'GET', None, token)
    if ok:
        print(f'5. 我的订单: PASS')
        print(f'   订单数量: {body.get("count", 0)}')
    else:
        print(f'5. 我的订单: FAIL - {status}')
else:
    print(f'5. 我的订单: SKIP')

print()

# 6. 提交交易哈希
if token and order_id:
    ok, status, body = test_api('submit_tx', f'/orders/{order_id}/submit_tx', 'POST', {
        'tx_hash': 'test_tx_hash_' + 'x' * 50
    }, token)
    if ok:
        print(f'6. 提交交易哈希: PASS')
        print(f'   结果: {body.get("message")}')
        print(f'   状态: {body.get("status")}')
    else:
        print(f'6. 提交交易哈希: FAIL - {status}')
else:
    print(f'6. 提交交易哈希: SKIP')

print()
print('=== 测试完成 ===')
