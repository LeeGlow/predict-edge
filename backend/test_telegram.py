"""
Telegram Bot 测试脚本
用法: python test_telegram.py
"""

import os
import sys
import asyncio
import httpx

async def test_telegram():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    print("=" * 50)
    print("PredictEdge Telegram Bot 测试")
    print("=" * 50)
    print()
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN 未设置")
        print("   请设置环境变量: set TELEGRAM_BOT_TOKEN=your_token")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID 未设置")
        print("   请设置环境变量: set TELEGRAM_CHAT_ID=your_chat_id")
        return False
    
    print(f"📱 Bot Token: {token[:10]}...{token[-6:]}")
    print(f"💬 Chat ID: {chat_id}")
    print()
    
    # 测试1: 获取Bot信息
    print("📋 测试1: 获取Bot信息")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://api.telegram.org/bot{token}/getMe"
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    bot_info = data["result"]
                    print(f"   Bot名称: {bot_info.get('first_name')}")
                    print(f"   Bot用户名: @{bot_info.get('username')}")
                    print(f"   ✅ Bot连接正常")
                else:
                    print(f"   ❌ 失败: {data}")
                    return False
            else:
                print(f"   ❌ HTTP {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False
    print()
    
    # 测试2: 发送测试消息
    print("✉️  测试2: 发送测试消息")
    test_message = """
🤖 <b>PredictEdge 测试消息</b>

恭喜！你的 Telegram Bot 配置成功！

<b>功能列表：</b>
• 实时价格警报推送
• 套利信号通知
• 每日市场早报

#预测市场 #套利工具 #PredictEdge
    """.strip()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": test_message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    print(f"   ✅ 消息发送成功")
                    print(f"   消息ID: {data['result']['message_id']}")
                else:
                    print(f"   ❌ 失败: {data}")
                    return False
            else:
                print(f"   ❌ HTTP {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False
    print()
    
    # 测试3: 模拟警报消息
    print("🔔 测试3: 模拟价格警报")
    alert_message = """
🔥 <b>价格警报</b> 🔴 高

DOGE涨幅概率单日暴涨15.2%

<b>事件：</b>DOGE本周涨幅超过20%?
<b>概率变化：</b>20.0% → 28.5%
<b>变化幅度：</b>+8.5%
<b>市场：</b>polymarket

#预测市场 #套利信号
    """.strip()
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": alert_message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }
            )
            if resp.status_code == 200:
                print(f"   ✅ 警报消息发送成功")
            else:
                print(f"   ⚠️  发送失败: {resp.status_code}")
    except Exception as e:
        print(f"   ⚠️  错误: {e}")
    print()
    
    print("=" * 50)
    print("🎉 所有测试通过！Telegram Bot 配置完成")
    print("=" * 50)
    print()
    print("下一步：")
    print("  1. 将 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID")
    print("     添加到 Render 环境变量")
    print("  2. 重启后端服务")
    print("  3. 享受实时警报推送！")
    print()
    return True

if __name__ == "__main__":
    success = asyncio.run(test_telegram())
    sys.exit(0 if success else 1)
