"""
PredictEdge - 预测市场套利工具
后端服务

功能：
1. 概率偏离警报
2. 历史胜率分析
3. 跨平台套利检测
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import asyncio
import logging
from collections import defaultdict
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PredictEdge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 数据模型 ====================

class MarketEvent(BaseModel):
    event_id: str
    title: str
    market: str  # "polymarket", "polymarkets_co_il", "custom"
    probability: float  # YES概率 0-100
    volume: float  # 成交量 USD
    deadline: datetime
    category: str  # "weather", "crypto", "sports", "politics", "other"
    created_at: datetime = datetime.utcnow()
    settled: bool = False
    outcome: Optional[bool] = None

class PriceAlert(BaseModel):
    id: str
    event_id: str
    alert_type: str  # "spike", "drop", "cross_threshold", "arbitrage"
    probability_before: float
    probability_after: float
    change: float
    timestamp: datetime
    message: str
    priority: str  # "low", "medium", "high"

class ArbitrageOpportunity(BaseModel):
    id: str
    events: List[Dict]  # 不同平台的事件
    price_diff: float  # 价差百分比
    action: str  # "buy_platform_a_sell_platform_b"
    estimated_profit: float  # 预估利润 %
    confidence: float  # 置信度 0-100
    timestamp: datetime
    status: str = "active"  # "active", "expired", "executed"

class AnalysisResult(BaseModel):
    event_id: str
    title: str
    category: str
    predicted_probability: float  # 基于历史的预测
    market_probability: float  # 当前市场价格
    deviation: float  # 偏差 = 市场 - 预测
    confidence: float  # 分析置信度
    recommendation: str  # "buy_yes", "buy_no", "hold"
    reasoning: str  # 分析理由
    historical_accuracy: float  # 该类型事件历史准确率

class HistoricalStat(BaseModel):
    category: str
    total_events: int
    avg_deviation: float  # 平均偏差
    hit_rate_over_70: float  # 概率>70%时的实际胜率
    hit_rate_under_30: float  # 概率<30%时的实际胜率
    best_threshold: float  # 最佳阈值
    sample_size: int

# ==================== 数据存储（内存演示，生产用数据库）====================

class DataStore:
    """内存数据存储"""
    
    def __init__(self):
        self.events: Dict[str, MarketEvent] = {}
        self.price_history: Dict[str, List[Dict]] = defaultdict(list)
        self.alerts: List[PriceAlert] = []
        self.arbitrage_opportunities: List[ArbitrageOpportunity] = []
        self.settled_events: List[MarketEvent] = []
        self.historical_stats: Dict[str, List[HistoricalStat]] = defaultdict(list)
        self.user_alerts: Dict[str, List[Dict]] = defaultdict(list)  # user_id -> alerts config
    
    def add_event(self, event: MarketEvent):
        self.events[event.event_id] = event
        # 记录价格历史
        self.price_history[event.event_id].append({
            "probability": event.probability,
            "volume": event.volume,
            "timestamp": datetime.utcnow()
        })
    
    def update_event(self, event_id: str, probability: float, volume: float):
        if event_id in self.events:
            old_prob = self.events[event_id].probability
            self.events[event_id].probability = probability
            self.events[event_id].volume = volume
            
            # 记录历史
            self.price_history[event_id].append({
                "probability": probability,
                "volume": volume,
                "timestamp": datetime.utcnow(),
                "change": probability - old_prob
            })
            
            # 检查是否触发警报
            self._check_alerts(event_id, old_prob, probability)
    
    def _check_alerts(self, event_id: str, old_prob: float, new_prob: float):
        """检查是否触发警报"""
        event = self.events[event_id]
        change = new_prob - old_prob
        
        # 大幅波动警报
        if abs(change) >= 10:
            alert = PriceAlert(
                id=f"alert_{event_id}_{datetime.utcnow().timestamp()}",
                event_id=event_id,
                alert_type="spike" if change > 0 else "drop",
                probability_before=old_prob,
                probability_after=new_prob,
                change=change,
                timestamp=datetime.utcnow(),
                message=f"🔥 {event.title[:30]}... 概率大幅变动 {change:+.1f}%",
                priority="high" if abs(change) >= 20 else "medium"
            )
            self.alerts.append(alert)
            logger.info(f"价格警报: {alert.message}")
        
        # 阈值突破警报
        thresholds = [30, 50, 70, 80, 90]
        for threshold in thresholds:
            if (old_prob < threshold <= new_prob) or (old_prob > threshold >= new_prob):
                alert = PriceAlert(
                    id=f"alert_thresh_{event_id}_{threshold}_{datetime.utcnow().timestamp()}",
                    event_id=event_id,
                    alert_type="cross_threshold",
                    probability_before=old_prob,
                    probability_after=new_prob,
                    change=change,
                    timestamp=datetime.utcnow(),
                    message=f"⚡ {event.title[:30]}... 突破 {threshold}% 阈值",
                    priority="medium"
                )
                self.alerts.append(alert)

data_store = DataStore()

# ==================== 数据源集成 ====================

async def fetch_polymarket_events() -> List[Dict]:
    """获取 Polymarket 事件"""
    # Polymarket GraphQL API
    url = "https://clob.polymarket.com/markets"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.error(f"获取Polymarket数据失败: {e}")
    
    return []

async def fetch_polymarkets_co_il_events() -> List[Dict]:
    """获取 polymarkets.co.il 事件（希伯来语站）"""
    # 这是网页爬取，需要解析HTML
    # 为了演示，返回一些模拟数据
    
    mock_events = [
        {
            "id": "weather_nyc_0627",
            "question": "6月27日纽约最高气温超过30°C?",
            "outcome": "Yes",
            "probability": 75.5,
            "volume": 218200,
            "deadline": datetime.utcnow() + timedelta(hours=24),
            "category": "weather"
        },
        {
            "id": "weather_hk_0627",
            "question": "6月27日香港最高气温超过33°C?",
            "outcome": "Yes",
            "probability": 68.2,
            "volume": 273200,
            "deadline": datetime.utcnow() + timedelta(hours=24),
            "category": "weather"
        },
        {
            "id": "crypto_btc_70000",
            "question": "BTC价格在6月27日前超过$70000?",
            "outcome": "Yes",
            "probability": 42.8,
            "volume": 892000,
            "deadline": datetime.utcnow() + timedelta(hours=48),
            "category": "crypto"
        },
        {
            "id": "crypto_eth_4000",
            "question": "ETH价格在6月30日前超过$4000?",
            "outcome": "Yes",
            "probability": 35.5,
            "volume": 456000,
            "deadline": datetime.utcnow() + timedelta(hours=72),
            "category": "crypto"
        },
        {
            "id": "sports_worldcup_2026",
            "question": "2026世界杯冠军是阿根廷?",
            "outcome": "Yes",
            "probability": 22.3,
            "volume": 1250000,
            "deadline": datetime.utcnow() + timedelta(days=365),
            "category": "sports"
        },
        {
            "id": "weather_london_0627",
            "question": "6月27日伦敦最高气温超过35°C?",
            "outcome": "Yes",
            "probability": 38.2,
            "volume": 312900,
            "deadline": datetime.utcnow() + timedelta(hours=24),
            "category": "weather"
        },
        {
            "id": "weather_tokyo_0627",
            "question": "6月27日东京最高气温超过28°C?",
            "outcome": "Yes",
            "probability": 89.5,
            "volume": 143300,
            "deadline": datetime.utcnow() + timedelta(hours=24),
            "category": "weather"
        },
        {
            "id": "crypto_sol_200",
            "question": "SOL价格在7月1日前超过$200?",
            "outcome": "Yes",
            "probability": 55.8,
            "volume": 234000,
            "deadline": datetime.utcnow() + timedelta(hours=96),
            "category": "crypto"
        }
    ]
    
    return mock_events

# ==================== 分析引擎 ====================

async def analyze_probability_deviation(event_id: str) -> Optional[AnalysisResult]:
    """分析概率偏差"""
    event = data_store.events.get(event_id)
    if not event:
        return None
    
    # 基于历史数据的简单分析
    category = event.category
    market_prob = event.probability
    
    # 模拟：获取该类型的历史准确率
    historical_accuracy = {
        "weather": 0.72,
        "crypto": 0.55,
        "sports": 0.68,
        "politics": 0.62,
        "other": 0.50
    }.get(category, 0.50)
    
    # 简单的偏差计算
    # 如果历史胜率>50%，市场概率可能被低估
    if historical_accuracy > 0.6 and market_prob < 70:
        predicted_prob = market_prob * (1 + (historical_accuracy - 0.5))
        recommendation = "buy_yes"
        reasoning = f"该类型事件历史胜率{historical_accuracy:.0%}，当前概率{market_prob:.1f}%可能被低估"
    elif historical_accuracy > 0.6 and market_prob > 70:
        predicted_prob = market_prob
        recommendation = "hold"
        reasoning = "概率已经较高，风险收益比下降"
    else:
        predicted_prob = market_prob
        recommendation = "hold"
        reasoning = "市场定价相对合理"
    
    deviation = market_prob - predicted_prob
    
    return AnalysisResult(
        event_id=event_id,
        title=event.title,
        category=category,
        predicted_probability=min(predicted_prob, 99.0),
        market_probability=market_prob,
        deviation=deviation,
        confidence=historical_accuracy * 100,
        recommendation=recommendation,
        reasoning=reasoning,
        historical_accuracy=historical_accuracy
    )

async def detect_arbitrage_opportunities() -> List[ArbitrageOpportunity]:
    """检测跨平台套利机会"""
    opportunities = []
    
    # 简化版：比较相同类型的事件
    # 实际需要更复杂的匹配逻辑
    
    crypto_events = [e for e in data_store.events.values() if e.category == "crypto"]
    weather_events = [e for e in data_store.events.values() if e.category == "weather"]
    
    # 检查加密货币事件之间的价差
    if len(crypto_events) >= 2:
        probs = [e.probability for e in crypto_events]
        if max(probs) - min(probs) > 15:
            # 找到最大价差
            max_event = max(crypto_events, key=lambda x: x.probability)
            min_event = min(crypto_events, key=lambda x: x.probability)
            
            opp = ArbitrageOpportunity(
                id=f"arb_crypto_{datetime.utcnow().timestamp()}",
                events=[
                    {"event": min_event.dict(), "action": "buy"},
                    {"event": max_event.dict(), "action": "sell"}
                ],
                price_diff=max(probs) - min(probs),
                action="多平台价差套利",
                estimated_profit=(max(probs) - min(probs)) / 2,
                confidence=65,
                timestamp=datetime.utcnow()
            )
            opportunities.append(opp)
    
    return opportunities

def calculate_historical_stats(category: str) -> HistoricalStat:
    """计算历史统计数据"""
    
    # 模拟历史数据
    # 实际需要从数据库读取真实结算事件
    
    mock_stats = {
        "weather": {
            "total_events": 156,
            "avg_deviation": 8.5,
            "hit_rate_over_70": 0.78,
            "hit_rate_under_30": 0.72,
            "best_threshold": 65
        },
        "crypto": {
            "total_events": 89,
            "avg_deviation": 12.3,
            "hit_rate_over_70": 0.65,
            "hit_rate_under_30": 0.61,
            "best_threshold": 60
        },
        "sports": {
            "total_events": 234,
            "avg_deviation": 7.2,
            "hit_rate_over_70": 0.75,
            "hit_rate_under_30": 0.70,
            "best_threshold": 68
        },
        "politics": {
            "total_events": 67,
            "avg_deviation": 15.8,
            "hit_rate_over_70": 0.58,
            "hit_rate_under_30": 0.55,
            "best_threshold": 55
        }
    }
    
    stats = mock_stats.get(category, {
        "total_events": 50,
        "avg_deviation": 10.0,
        "hit_rate_over_70": 0.65,
        "hit_rate_under_30": 0.65,
        "best_threshold": 60
    })
    
    return HistoricalStat(
        category=category,
        total_events=stats["total_events"],
        avg_deviation=stats["avg_deviation"],
        hit_rate_over_70=stats["hit_rate_over_70"],
        hit_rate_under_30=stats["hit_rate_under_30"],
        best_threshold=stats["best_threshold"],
        sample_size=stats["total_events"]
    )

# ==================== API 端点 ====================

@app.get("/")
async def root():
    return {
        "name": "PredictEdge API",
        "version": "1.0.0",
        "description": "预测市场套利工具后端"
    }

@app.get("/events")
async def get_events(
    category: Optional[str] = None,
    active_only: bool = True
):
    """获取所有事件"""
    events = list(data_store.events.values())
    
    if active_only:
        events = [e for e in events if not e.settled and e.deadline > datetime.utcnow()]
    
    if category:
        events = [e for e in events if e.category == category]
    
    return {
        "events": [e.dict() for e in events],
        "count": len(events)
    }

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """获取单个事件详情"""
    event = data_store.events.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event.dict()

@app.get("/events/{event_id}/analysis")
async def analyze_event(event_id: str):
    """分析单个事件的概率偏差"""
    analysis = await analyze_probability_deviation(event_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Event not found")
    return analysis

@app.get("/events/{event_id}/history")
async def get_price_history(event_id: str, limit: int = 50):
    """获取事件价格历史"""
    history = data_store.price_history.get(event_id, [])
    return {
        "event_id": event_id,
        "history": history[-limit:],
        "count": len(history)
    }

@app.get("/alerts")
async def get_alerts(
    limit: int = 20,
    priority: Optional[str] = None
):
    """获取价格警报"""
    alerts = data_store.alerts
    
    if priority:
        alerts = [a for a in alerts if a.priority == priority]
    
    return {
        "alerts": [a.dict() for a in alerts[-limit:]],
        "count": len(alerts)
    }

@app.get("/arbitrage")
async def get_arbitrage_opportunities():
    """获取套利机会"""
    opportunities = await detect_arbitrage_opportunities()
    return {
        "opportunities": [o.dict() for o in opportunities],
        "count": len(opportunities)
    }

@app.get("/stats/{category}")
async def get_category_stats(category: str):
    """获取分类历史统计"""
    stats = calculate_historical_stats(category)
    return stats

@app.get("/stats")
async def get_all_stats():
    """获取所有分类统计"""
    categories = ["weather", "crypto", "sports", "politics", "other"]
    return {
        "stats": {cat: calculate_historical_stats(cat).dict() for cat in categories}
    }

@app.post("/alerts/subscribe")
async def subscribe_alerts(config: Dict):
    """订阅警报配置"""
    user_id = config.get("user_id", "anonymous")
    data_store.user_alerts[user_id].append(config)
    return {"status": "success", "message": "警报订阅成功"}

# ==================== 数据更新任务 ====================

async def update_market_data():
    """后台任务：定期更新市场数据"""
    while True:
        try:
            # 获取 polymarkets.co.il 事件
            events_data = await fetch_polymarkets_co_il_events()
            
            for data in events_data:
                event = MarketEvent(
                    event_id=data["id"],
                    title=data["question"],
                    market="polymarkets_co_il",
                    probability=data["probability"],
                    volume=data["volume"],
                    deadline=data["deadline"],
                    category=data["category"]
                )
                
                # 更新或添加
                if event.event_id in data_store.events:
                    data_store.update_event(
                        event.event_id,
                        event.probability,
                        event.volume
                    )
                else:
                    data_store.add_event(event)
            
            logger.info(f"更新了 {len(events_data)} 个事件")
            
        except Exception as e:
            logger.error(f"更新市场数据失败: {e}")
        
        await asyncio.sleep(60)  # 每分钟更新

@app.on_event("startup")
async def startup():
    """启动时初始化"""
    # 启动后台数据更新任务
    asyncio.create_task(update_market_data())
    
    # 预加载一些事件
    events_data = await fetch_polymarkets_co_il_events()
    for data in events_data:
        event = MarketEvent(
            event_id=data["id"],
            title=data["question"],
            market="polymarkets_co_il",
            probability=data["probability"],
            volume=data["volume"],
            deadline=data["deadline"],
            category=data["category"]
        )
        data_store.add_event(event)
    
    logger.info(f"初始化完成，加载了 {len(events_data)} 个事件")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)