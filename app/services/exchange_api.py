import os
import json
import httpx
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量（如 API 密钥）
load_dotenv()

# 定义数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DAILY_RATES_FILE = os.path.join(DATA_DIR, "daily_rates.json")
HISTORY_RECORDS_FILE = os.path.join(DATA_DIR, "history_records.json")

# 获取 API 密钥
EXCHANGE_API_KEY = os.getenv("EXCHANGE_API_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

# 默认回退汇率（当 API 不可用时使用）
DEFAULT_RATES = {
    "USD": 1, "CNY": 7.25, "EUR": 0.92, "GBP": 0.79, "JPY": 150.0,
    "HKD": 7.82, "AUD": 1.52, "CAD": 1.36, "SGD": 1.35, "CHF": 0.88
}

class ExchangeService:
    """
    汇率服务类。
    负责处理所有与汇率相关的业务逻辑，包括：
    1. 获取实时汇率（带缓存）
    2. 获取历史数据
    3. 获取市场新闻
    4. 货币转换计算
    5. 管理用户操作历史记录
    """
    def __init__(self):
        # 初始化时加载本地缓存的汇率数据
        self.rates_cache = self._load_json(DAILY_RATES_FILE)
        self.news_cache = {} # 新闻内存缓存
        self.last_news_fetch = 0 # 上次获取新闻的时间戳

    def _load_json(self, filepath):
        """
        辅助方法：读取 JSON 文件。
        如果文件不存在或读取失败，返回空字典。
        """
        if not os.path.exists(filepath):
            return {}
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save_json(self, filepath, data):
        """
        辅助方法：保存数据到 JSON 文件。
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存JSON到 {filepath} 错误: {e}")

    async def get_realtime_rates(self):
        """
        获取实时汇率。
        策略：
        1. 检查内存/文件缓存是否在有效期内（5分钟）。
        2. 如果缓存有效，直接返回缓存数据。
        3. 如果缓存过期，请求外部 API。
        4. 如果 API 请求失败，回退到旧缓存或默认静态汇率。
        """
        now = time.time()
        last_update = self.rates_cache.get("time_last_update_unix", 0)
        
        # 如果缓存新鲜（小于5分钟 / 300秒）
        if now - last_update < 300 and "conversion_rates" in self.rates_cache:
            return self.rates_cache["conversion_rates"]

        # 从 ExchangeRate-API 获取最新数据
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/USD"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("result") == "success":
                        # 更新缓存并保存到文件
                        self.rates_cache = data
                        self._save_json(DAILY_RATES_FILE, data)
                        return data["conversion_rates"]
        except Exception as e:
            print(f"API 错误: {e}")
        
        # 如果 API 失败，尝试使用旧缓存
        if "conversion_rates" in self.rates_cache:
            return self.rates_cache["conversion_rates"]
            
        # 最后手段：使用硬编码的默认汇率
        return DEFAULT_RATES

    async def get_historical_data(self, base="USD", target="CNY", days=30):
        """
        获取历史汇率趋势数据。
        注意：由于免费版 API 通常不支持历史数据查询，这里使用模拟算法生成逼真的波动数据。
        基于当前实时汇率，生成过去 N 天的随机波动数据。
        """
        current_rates = await self.get_realtime_rates()
        base_rate = current_rates.get(base, 1.0)
        target_rate = current_rates.get(target, 1.0)
        
        # 计算当前的交叉汇率
        rate = target_rate / base_rate
        
        dates = []
        values = []
        import random
        
        # 生成过去 days 天的数据
        for i in range(days):
            d = datetime.now() - timedelta(days=days-i)
            dates.append(d.strftime("%Y-%m-%d"))
            # 随机波动 +/- 2%
            fluctuation = random.uniform(0.98, 1.02)
            values.append(round(rate * fluctuation, 4))
            
        return {"labels": dates, "data": values, "rate": rate}

    async def get_news(self):
        """
        获取外汇市场新闻。
        使用 Alpha Vantage API。
        缓存策略：1小时（3600秒）更新一次，避免频繁消耗 API 配额。
        """
        now = time.time()
        # 如果缓存有效（1小时内），直接返回
        if now - self.last_news_fetch < 3600 and self.news_cache:
            return self.news_cache

        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&topic=forex&apikey={ALPHAVANTAGE_API_KEY}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if "feed" in data:
                        # 只取前5条新闻
                        news_items = []
                        for item in data["feed"][:5]:
                            news_items.append({
                                "title": item.get("title"),
                                "url": item.get("url"),
                                "source": item.get("source"),
                                "summary": item.get("summary", "")[:100] + "..."
                            })
                        self.news_cache = news_items
                        self.last_news_fetch = now
                        return news_items
        except Exception as e:
            print(f"新闻 API 错误: {e}")
            
        return self.news_cache if self.news_cache else []

    def convert_currency(self, amount, from_curr, to_curr, rates):
        """
        货币转换计算逻辑。
        公式：(金额 / 源货币汇率) * 目标货币汇率
        所有汇率都是基于 USD 的。
        """
        if from_curr not in rates or to_curr not in rates:
            return 0.0
        
        # 先转换为 USD (基准)
        amount_in_usd = amount / rates[from_curr]
        # 再转换为目标货币
        return round(amount_in_usd * rates[to_curr], 6)

    def get_history_records(self, filter_type=None):
        """
        获取用户的操作历史记录。
        支持按类型筛选（如只看 'purchase' 记录）。
        """
        records = self._load_json(HISTORY_RECORDS_FILE)
        if filter_type:
            return [r for r in records if r.get("type") == filter_type]
        return records

    def add_history_record(self, record_type, details):
        """
        添加一条新的历史记录。
        记录包含：ID、时间、类型、详情。
        新记录会被插入到列表最前面。
        """
        records = self._load_json(HISTORY_RECORDS_FILE)
        new_record = {
            "id": int(time.time() * 1000),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": record_type, # 'purchase', 'sale', 'settle', 'warning'
            "details": details
        }
        records.insert(0, new_record) # 添加到顶部
        self._save_json(HISTORY_RECORDS_FILE, records)
        return new_record

    def clear_history_records(self):
        """
        清空所有历史记录。
        """
        self._save_json(HISTORY_RECORDS_FILE, [])

# 创建全局单例实例
exchange_service = ExchangeService()
