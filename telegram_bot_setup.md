# PredictEdge Telegram Bot 配置指南

## 快速开始

### 1. 创建 Telegram Bot
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置 Bot 名称和用户名
4. 获得 Bot Token（格式：`123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`）

### 2. 获取 Chat ID
1. 在 Telegram 中搜索你刚创建的 Bot，发送任意消息
2. 访问：`https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在返回的 JSON 中找到 `chat.id` 字段

### 3. 配置环境变量

#### 本地开发
创建 `.env` 文件在 `backend/` 目录下：
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
SECRET_KEY=your-super-secret-key-change-in-production
```

#### Render 部署
在 Render Dashboard → Environment 中添加：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `SECRET_KEY`

### 4. 测试 Bot
运行测试脚本：
```bash
cd backend
python test_telegram.py
```

## 警报推送规则

| 警报类型 | 触发条件 | 优先级 | Telegram推送 |
|---------|---------|--------|-------------|
| 价格暴涨 | 单日涨幅 ≥ 20% | 🔴 高 | ✅ 立即推送 |
| 价格暴跌 | 单日跌幅 ≥ 20% | 🔴 高 | ✅ 立即推送 |
| 大幅波动 | 单日涨跌幅 10-20% | 🟡 中 | ❌ 仅APP显示 |
| 阈值突破 | 突破30/50/70/80/90% | 🟡 中 | ❌ 仅APP显示 |

## 消息格式示例

```
🔥 价格警报 🔴 高

DOGE本周涨幅概率单日暴涨15.2%

事件：DOGE本周涨幅超过20%?
概率变化：20.0% → 28.5%
变化幅度：+8.5%
市场：polymarket

#预测市场 #套利信号
```

## 进阶功能（待开发）

- [ ] 用户自定义警报阈值
- [ ] 自选事件监控
- [ ] 每日早报/晚报推送
- [ ] 套利信号定时推送
- [ ] 多语言支持
- [ ] 订阅管理（通过Bot升级/续费）
