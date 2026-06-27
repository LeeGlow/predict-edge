import requests
import json

BASE = 'http://localhost:8002/api'

print('=' * 50)
print('PredictEdge API 全面测试')
print('=' * 50)
print()

# 测试1: 健康检查
print('📊 测试1: 健康检查')
try:
    r = requests.get('http://localhost:8002/health')
    print(f'   状态: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'   事件数: {data["events_count"]}')
        print(f'   ✅ 通过')
    else:
        print(f'   ❌ 失败: {r.text}')
except Exception as e:
    print(f'   ❌ 错误: {e}')
print()

# 测试2: 注册新用户
print('👤 测试2: 用户注册')
try:
    import random
    username = f'testuser{random.randint(1000, 9999)}'
    r = requests.post(f'{BASE}/auth/register', json={
        'username': username,
        'password': 'test123456'
    })
    print(f'   用户名: {username}')
    print(f'   状态: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        token = data['access_token']
        user = data['user']
        print(f'   用户ID: {user["id"]}')
        print(f'   订阅: {user["subscription_name"]}')
        print(f'   ✅ 注册成功')
    else:
        print(f'   ❌ 失败: {r.text}')
        token = None
        user = None
except Exception as e:
    print(f'   ❌ 错误: {e}')
    token = None
    user = None
print()

# 测试3: 登录
print('🔐 测试3: 用户登录')
if token:
    try:
        r2 = requests.post(f'{BASE}/auth/login', json={
            'username': username,
            'password': 'test123456'
        })
        print(f'   状态: {r2.status_code}')
        if r2.status_code == 200:
            data2 = r2.json()
            token2 = data2['access_token']
            print(f'   ✅ 登录成功')
            
            # 测试4: 获取用户信息
            print()
            print('👤 测试4: 获取当前用户信息')
            r3 = requests.get(f'{BASE}/auth/me', headers={
                'Authorization': f'Bearer {token2}'
            })
            print(f'   状态: {r3.status_code}')
            if r3.status_code == 200:
                me = r3.json()
                print(f'   用户名: {me["username"]}')
                print(f'   订阅等级: {me["subscription_name"]}')
                print(f'   每日限额: {me["daily_events_limit"]}')
                print(f'   ✅ 通过')
            else:
                print(f'   ❌ 失败: {r3.text}')
        else:
            print(f'   ❌ 登录失败: {r2.text}')
            token2 = token
    except Exception as e:
        print(f'   ❌ 错误: {e}')
        token2 = token
else:
    print('   ⏭️  跳过（注册失败）')
    token2 = None
print()

# 测试5: 获取事件列表
print('📋 测试5: 获取事件列表')
if token2:
    try:
        r4 = requests.get(f'{BASE}/events', headers={
            'Authorization': f'Bearer {token2}'
        })
        print(f'   状态: {r4.status_code}')
        if r4.status_code == 200:
            events_data = r4.json()
            print(f'   事件数: {events_data["count"]}')
            if events_data['events']:
                first = events_data['events'][0]
                print(f'   第一个: {first["title"][:40]}...')
                print(f'   概率: {first["probability"]}%')
            print(f'   ✅ 通过')
        else:
            print(f'   ❌ 失败: {r4.text}')
    except Exception as e:
        print(f'   ❌ 错误: {e}')
else:
    print('   ⏭️  跳过（未登录）')
print()

# 测试6: 获取订阅计划
print('💎 测试6: 获取订阅计划')
try:
    r5 = requests.get(f'{BASE}/subscription/plans')
    print(f'   状态: {r5.status_code}')
    if r5.status_code == 200:
        plans = r5.json()['plans']
        print(f'   计划数: {len(plans)}')
        for tier, info in plans.items():
            print(f'   - {info["name"]}: ${info["price"]}/月')
        print(f'   ✅ 通过')
    else:
        print(f'   ❌ 失败: {r5.text}')
except Exception as e:
    print(f'   ❌ 错误: {e}')
print()

# 测试7: 统计数据
print('📊 测试7: 获取统计数据')
if token2:
    try:
        r6 = requests.get(f'{BASE}/stats', headers={
            'Authorization': f'Bearer {token2}'
        })
        print(f'   状态: {r6.status_code}')
        if r6.status_code == 200:
            stats = r6.json()['stats']
            print(f'   分类数: {len(stats)}')
            print(f'   ✅ 通过')
        else:
            print(f'   ❌ 失败: {r6.text}')
    except Exception as e:
        print(f'   ❌ 错误: {e}')
else:
    print('   ⏭️  跳过（未登录）')
print()

print('=' * 50)
print('测试完成！')
print('=' * 50)
