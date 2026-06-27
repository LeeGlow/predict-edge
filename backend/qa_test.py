import urllib.request
import json
import random

base = 'http://127.0.0.1:8002/api'

def test(endpoint, method='GET', data=None, token=None):
    try:
        headers = {}
        if data:
            headers['Content-Type'] = 'application/json'
            body = json.dumps(data).encode()
        else:
            body = None
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        req = urllib.request.Request(f'{base}{endpoint}', data=body, headers=headers, method=method)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        return True, resp.status, result
    except Exception as e:
        return False, str(e), None

print('=== 全面QA测试 ===\n')

# 1. 健康检查
ok, status, body = test('/health')
print(f'1. 健康检查: {"PASS" if ok else "FAIL"} status={status}')

# 2. 事件列表
ok, status, body = test('/events?category=all&limit=10')
event_count = len(body.get('events', [])) if ok and isinstance(body, dict) else 0
print(f'2. 事件列表: {"PASS" if ok else "FAIL"} status={status} events={event_count}')

# 3. 统计数据
ok, status, body = test('/stats')
print(f'3. 统计数据: {"PASS" if ok else "FAIL"} status={status}')

# 4. 定价方案
ok, status, body = test('/subscription/plans')
plans_count = len(body.get('plans', {})) if ok else 0
print(f'4. 定价方案: {"PASS" if ok else "FAIL"} status={status} plans={plans_count}')

# 5. 注册
username = f'qa_user_{random.randint(10000, 99999)}'
ok, status, body = test('/auth/register', 'POST', {
    'username': username,
    'password': 'test123456',
    'email': f'{username}@test.com'
})
user_name = body.get('user', {}).get('username', '') if ok else ''
print(f'5. 用户注册: {"PASS" if ok else "FAIL"} status={status} user={user_name}')

token = None
if ok:
    token = body['access_token']
    
    # 6. 获取用户信息
    ok2, status2, body2 = test('/auth/me', token=token)
    tier = body2.get('subscription_tier', '') if ok2 else ''
    print(f'6. 用户信息: {"PASS" if ok2 else "FAIL"} status={status2} tier={tier}')
    
    # 7. 套利信号
    ok3, status3, body3 = test('/arbitrage?limit=10', token=token)
    signals_count = len(body3) if ok3 and isinstance(body3, list) else 'N/A'
    print(f'7. 套利信号: {"PASS" if ok3 else "FAIL"} status={status3} signals={signals_count}')
    
    # 8. 登录测试
    ok4, status4, body4 = test('/auth/login', 'POST', {
        'username': username,
        'password': 'test123456'
    })
    print(f'8. 用户登录: {"PASS" if ok4 else "FAIL"} status={status4}')

# 9. 警报
ok, status, body = test('/alerts')
alerts_count = len(body) if ok and isinstance(body, list) else 'N/A'
print(f'9. 警报列表: {"PASS" if ok else "FAIL"} status={status} alerts={alerts_count}')

print('\n=== 测试完成 ===')
