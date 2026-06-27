import requests

BASE = 'http://localhost:8002/api'

# 登录admin
r = requests.post(f'{BASE}/auth/login', json={'username': 'admin', 'password': 'admin123456'})
print(f'登录: {r.status_code}')
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 测试用户列表
r = requests.get(f'{BASE}/admin/users', headers=headers)
print(f'\n用户列表: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  总数: {data.get("total")}')
    print(f'  当前页: {data.get("count")}')
    if data.get('users'):
        print(f'  第一个用户: {data["users"][0]["username"]} - {data["users"][0].get("tier_name", data["users"][0]["subscription_tier"])}')

# 测试搜索用户
r = requests.get(f'{BASE}/admin/users?search=test', headers=headers)
print(f'\n搜索用户(test): {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  搜索结果: {data.get("count")} 个')

# 测试数据面板
r = requests.get(f'{BASE}/admin/dashboard', headers=headers)
print(f'\n数据面板: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  总用户: {data.get("total_users")}')
    print(f'  付费用户: {data.get("paid_users")}')
    print(f'  待处理订单: {data.get("pending_orders")}')
    print(f'  总收入: ${data.get("total_revenue")}')

# 测试设置用户订阅
test_user_id = 1  # 假设ID=1存在
r = requests.post(f'{BASE}/admin/users/{test_user_id}/subscription', 
                  json={'tier': 'pro', 'days': 30},
                  headers=headers)
print(f'\n设置用户订阅: {r.status_code}')
if r.status_code == 200:
    print(f'  成功: {r.json().get("message")}')
else:
    print(f'  错误: {r.text}')
