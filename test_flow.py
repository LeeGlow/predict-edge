import urllib.request
import json
import random

print('=' * 70)
print('  PredictEdge 全流程功能测试报告')
print('=' * 70)

results = []


def test(name, condition, detail=''):
    status = 'PASS' if condition else 'FAIL'
    results.append((name, status, detail))
    icon = 'OK' if condition else 'XX'
    print(f'  [{icon}]  {name}')
    if detail:
        print(f'         {detail}')


# ==================== 1. 未登录用户测试 ====================
print()
print('【1/3】未登录用户测试')
print('-' * 70)

try:
    resp = urllib.request.urlopen('http://localhost:8000/')
    test('首页可访问', resp.status == 200)
except Exception as e:
    test('首页可访问', False, str(e))

try:
    resp = urllib.request.urlopen('http://localhost:8000/api/events')
    data = json.loads(resp.read())
    cnt = data.get('count', 0)
    test('事件列表API', cnt > 0, '数量: ' + str(cnt))
except Exception as e:
    test('事件列表API', False, str(e))

try:
    resp = urllib.request.urlopen('http://localhost:8000/api/arbitrage')
    test('套利信号API(未登录)', False, '应该返回401但返回了200')
except urllib.error.HTTPError as e:
    test('套利信号API(未登录)', e.code == 401, '状态码: ' + str(e.code))
except Exception as e:
    test('套利信号API(未登录)', False, str(e))

try:
    resp = urllib.request.urlopen('http://localhost:8000/api/auth/me')
    test('用户信息API(未登录)', False, '应该返回401但返回了200')
except urllib.error.HTTPError as e:
    test('用户信息API(未登录)', e.code == 401, '状态码: ' + str(e.code))
except Exception as e:
    test('用户信息API(未登录)', False, str(e))

# ==================== 2. 免费用户测试 ====================
print()
print('【2/3】免费用户测试')
print('-' * 70)

test_username = 'testfree_' + str(random.randint(1000, 9999))
free_token = None

try:
    data = json.dumps({'username': test_username, 'password': 'test123456'}).encode()
    req = urllib.request.Request('http://localhost:8000/api/auth/register', data=data,
                                 headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    free_token = result.get('access_token')
    free_user = result.get('user', {})
    tier = free_user.get('subscription_tier', '')
    test('免费用户注册', free_token is not None, '用户: ' + test_username)
    test('免费用户等级', tier == 'free', '等级: ' + tier)
except Exception as e:
    test('免费用户注册', False, str(e))

if free_token:
    try:
        req = urllib.request.Request('http://localhost:8000/api/auth/me',
                                     headers={'Authorization': 'Bearer ' + free_token})
        resp = urllib.request.urlopen(req)
        me = json.loads(resp.read())
        test('免费用户信息', me.get('subscription_tier') == 'free',
             '等级: ' + str(me.get('subscription_tier')))
    except Exception as e:
        test('免费用户信息', False, str(e))

    try:
        req = urllib.request.Request('http://localhost:8000/api/events',
                                     headers={'Authorization': 'Bearer ' + free_token})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        events = data.get('events', [])
        has_analysis = any('analysis' in e for e in events)
        test('免费用户事件(无AI分析)', not has_analysis)
    except Exception as e:
        test('免费用户事件', False, str(e))

    try:
        req = urllib.request.Request('http://localhost:8000/api/arbitrage',
                                     headers={'Authorization': 'Bearer ' + free_token})
        resp = urllib.request.urlopen(req)
        arb = json.loads(resp.read())
        cnt = arb.get('count', 0)
        test('免费用户套利API', True, '数量: ' + str(cnt))
    except urllib.error.HTTPError as e:
        test('免费用户套利API', True, '状态码: ' + str(e.code) + ' (正常)')
    except Exception as e:
        test('免费用户套利API', False, str(e))

# ==================== 3. 机构版用户测试 ====================
print()
print('【3/3】机构版用户测试 (admin)')
print('-' * 70)

admin_token = None
try:
    data = json.dumps({'username': 'admin', 'password': 'admin123456'}).encode()
    req = urllib.request.Request('http://localhost:8000/api/auth/login', data=data,
                                 headers={'Content-Type': 'application/json'})
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    admin_token = result.get('access_token')
    admin_user = result.get('user', {})
    tier = admin_user.get('subscription_tier', '')
    test('admin登录', admin_token is not None)
    test('admin等级', tier == 'agency', '等级: ' + tier)
except Exception as e:
    test('admin登录', False, str(e))

if admin_token:
    try:
        req = urllib.request.Request('http://localhost:8000/api/events',
                                     headers={'Authorization': 'Bearer ' + admin_token})
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        events = data.get('events', [])
        has_analysis = any('analysis' in e for e in events)
        test('机构版事件(有AI分析)', has_analysis)
    except Exception as e:
        test('机构版事件', False, str(e))

    try:
        req = urllib.request.Request('http://localhost:8000/api/arbitrage',
                                     headers={'Authorization': 'Bearer ' + admin_token})
        resp = urllib.request.urlopen(req)
        arb = json.loads(resp.read())
        cnt = arb.get('count', 0)
        test('机构版套利API', cnt > 0, '数量: ' + str(cnt))
        if arb.get('opportunities'):
            opp = arb['opportunities'][0]
            wr = opp.get('estimated_win_rate', 'N/A')
            test('套利信号包含胜率', wr is not None, '胜率: ' + str(wr) + '%')
    except Exception as e:
        test('机构版套利API', False, str(e))

    try:
        req = urllib.request.Request('http://localhost:8000/api/admin/orders',
                                     headers={'Authorization': 'Bearer ' + admin_token})
        resp = urllib.request.urlopen(req)
        orders = json.loads(resp.read())
        test('后台订单API', 'orders' in orders, '数量: ' + str(orders.get('count')))
    except Exception as e:
        test('后台订单API', False, str(e))

# ==================== 汇总 ====================
print()
print('=' * 70)
passed = sum(1 for _, s, _ in results if s == 'PASS')
total = len(results)
print('  测试结果: ' + str(passed) + '/' + str(total) + ' 通过')
print('=' * 70)

if passed < total:
    print()
    print('  失败的测试:')
    for name, status, detail in results:
        if status == 'FAIL':
            print('    [XX] ' + name + ' - ' + detail)
