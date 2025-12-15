from fastapi import FastAPI, Request, Form, Query, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.exchange_api import exchange_service
from app.locales import translations
import os

app = FastAPI(title="Exchange Rate Dashboard")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板
templates = Jinja2Templates(directory="templates")

# 下拉菜单的常用货币
CURRENCIES = ["USD", "CNY", "EUR", "GBP", "JPY", "HKD", "AUD", "CAD", "SGD", "CHF", "INR", "RUB", "KRW", "THB", "VND", "MYR", "IDR", "PHP", "TWD", "NZD"]

# 获取语言依赖
def get_lang(request: Request):
    """
    从请求的 Cookie 中获取语言设置。
    如果 Cookie 中没有设置语言，默认返回 'zh' (中文)。
    """
    return request.cookies.get("lang", "zh")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, lang: str = Query(None)):
    """
    首页路由。
    渲染 index.html 模板，并根据查询参数或 Cookie 设置语言。
    """
    # 如果查询参数中有 lang，则设置 cookie
    response_lang = lang if lang in translations else request.cookies.get("lang", "zh")
    trans = translations[response_lang]
    
    response = templates.TemplateResponse("index.html", {
        "request": request, 
        "currencies": CURRENCIES, 
        "trans": trans,
        "current_lang": response_lang
    })
    if lang:
        response.set_cookie(key="lang", value=lang)
    return response

@app.get("/api/realtime", response_class=HTMLResponse)
async def get_realtime_rates(request: Request, lang: str = Depends(get_lang)):
    """
    获取实时汇率数据的 HTML 片段。
    用于 HTMX 局部刷新汇率表格。
    """
    trans = translations.get(lang, translations["zh"])
    rates = await exchange_service.get_realtime_rates()
    # 过滤主要货币进行显示
    display_rates = {k: v for k, v in rates.items() if k in CURRENCIES}
    return templates.TemplateResponse("partials/rates_table.html", {"request": request, "rates": display_rates, "trans": trans})

@app.get("/api/rates/json")
async def get_rates_json():
    """
    获取实时汇率数据的 JSON 格式。
    用于前端图表或其他需要原始数据的场景。
    """
    rates = await exchange_service.get_realtime_rates()
    return JSONResponse(content=rates)

@app.post("/api/convert", response_class=HTMLResponse)
async def convert_currency(request: Request, amount: float = Form(...), from_curr: str = Form(...), to_curr: str = Form(...), lang: str = Depends(get_lang)):
    """
    货币转换计算。
    接收金额、源货币、目标货币，返回计算结果的 HTML 片段。
    """
    trans = translations.get(lang, translations["zh"])
    rates = await exchange_service.get_realtime_rates()
    result = exchange_service.convert_currency(amount, from_curr, to_curr, rates)
    return f"<div class='alert alert-success mt-3'>{trans['result']}: {amount} {from_curr} = <strong>{result} {to_curr}</strong></div>"

@app.get("/api/news", response_class=HTMLResponse)
async def get_news(request: Request, lang: str = Depends(get_lang)):
    """
    获取市场新闻的 HTML 片段。
    用于 HTMX 局部刷新新闻列表。
    """
    trans = translations.get(lang, translations["zh"])
    news = await exchange_service.get_news()
    return templates.TemplateResponse("partials/news_list.html", {"request": request, "news": news, "trans": trans})

@app.get("/api/history")
async def get_history(base: str = Query("USD"), target: str = Query("CNY"), days: int = Query(30)):
    """
    获取历史汇率数据的 JSON 格式。
    用于前端绘制历史趋势图表。
    """
    data = await exchange_service.get_historical_data(base, target, days)
    return JSONResponse(content=data)

@app.post("/api/purchase/compare", response_class=HTMLResponse)
async def calculate_purchase_cost(request: Request, lang: str = Depends(get_lang)):
    """
    采购成本比较计算。
    接收多个供应商的报价（金额和货币），统一换算成人民币进行比较，找出最低价。
    """
    trans = translations.get(lang, translations["zh"])
    # 注意：FastAPI 表单列表处理可能需要特定的前端命名，如 amounts&amounts
    # 为了在 HTMX 中简化，我们可能会以不同方式接收它们，或者如果复杂则手动解析表单数据。
    # 让我们假设简单的单项计算或如果可能处理列表。
    # 实际上，对于动态列表，接受 JSON 正文或解析原始表单更容易。
    # 但是 HTMX 发送表单数据。让我们简化：用户添加行，提交表单。
    # 我们将直接从请求中读取表单数据以获取动态字段。
    form_data = await request.form()
    
    items = []
    rates = await exchange_service.get_realtime_rates()
    cny_rate = rates.get("CNY", 1.0) # 假设我们想要 CNY 的成本
    
    # 手动提取列表，因为键可能是重复的 'amount' 和 'currency'
    raw_amounts = form_data.getlist("amount")
    raw_currencies = form_data.getlist("currency")
    
    total_cny = 0
    results = []
    
    for amt, curr in zip(raw_amounts, raw_currencies):
        try:
            val = float(amt)
            # 先转换为 USD 然后转换为 CNY
            usd_val = val / rates.get(curr, 1.0)
            cny_val = usd_val * cny_rate
            results.append({
                "amount": val,
                "currency": curr,
                "cny_cost": round(cny_val, 2)
            })
            total_cny += cny_val
        except:
            continue
            
    # 找到最佳（最低成本） - 等等，这个逻辑假设比较同一项目的选项？
    # 还是汇总 BOM？提示说“比较多个供应商报价...高亮最低”。
    # 所以是选项。
    
    if results:
        min_cost = min(r["cny_cost"] for r in results)
        for r in results:
            r["is_best"] = (r["cny_cost"] == min_cost)
            
    # 记录到历史
    details = f"{trans['total_options']}: {len(results)}, {trans['best_price_cny']}: ¥{min_cost if results else 0}"
    exchange_service.add_history_record("purchase_cost_compare", details)

    response = templates.TemplateResponse("partials/purchase_result.html", {"request": request, "results": results, "trans": trans})
    response.headers["HX-Trigger"] = "historyChanged"
    return response

@app.post("/api/sale/price", response_class=HTMLResponse)
async def calculate_sale_price(request: Request, lang: str = Depends(get_lang)):
    """
    智能定价计算。
    根据成本（CNY）和目标市场的利润率，计算出在不同市场的建议售价（当地货币）。
    """
    trans = translations.get(lang, translations["zh"])
    # 列表的类似处理
    form_data = await request.form()
    
    try:
        cost_cny = float(form_data.get("cost_cny", 0))
    except ValueError:
        return HTMLResponse(f"<div class='alert alert-danger'>{trans['invalid_cost']}</div>")

    raw_markets = form_data.getlist("market") # 例如 USD, EUR
    raw_margins = form_data.getlist("margin") # 例如 20 代表 20%
    
    rates = await exchange_service.get_realtime_rates()
    cny_rate = rates.get("CNY", 1.0)
    
    results = []
    for mkt, margin in zip(raw_markets, raw_margins):
        try:
            margin_pct = float(margin) / 100.0
            target_price_cny = cost_cny * (1 + margin_pct)
            
            # 转换 CNY -> USD -> 目标市场货币
            # CNY -> USD
            price_usd = target_price_cny / cny_rate
            # USD -> 目标
            price_local = price_usd * rates.get(mkt, 1.0)
            
            results.append({
                "market": mkt,
                "margin": margin,
                "price_local": round(price_local, 2),
                "price_cny": round(target_price_cny, 2)
            })
        except:
            continue
            
    # details = f"{trans['cost']}: ¥{cost_cny}, {trans['markets_count']}: {len(results)}"
    # 构造更详细的记录
    res_strs = [f"{r['market']} {r['price_local']} ({r['margin']}%)" for r in results]
    details = f"{trans['cost']} ¥{cost_cny} -> {', '.join(res_strs)}"
    exchange_service.add_history_record("smart_pricing", details)
    
    response = templates.TemplateResponse("partials/sale_result.html", {"request": request, "results": results, "trans": trans})
    response.headers["HX-Trigger"] = "historyChanged"
    return response

@app.post("/api/warning/add", response_class=HTMLResponse)
async def add_warning(request: Request, lang: str = Depends(get_lang)):
    """
    添加汇率预警。
    设置当汇率达到特定阈值时的提醒（目前仅记录到历史记录中）。
    """
    trans = translations.get(lang, translations["zh"])
    form_data = await request.form()
    
    base = form_data.get("base_currency")
    target = form_data.get("target_currency")
    
    if base and target:
        pair = f"{base}/{target}"
    else:
        pair = form_data.get("pair", "USD/CNY")

    condition = form_data.get("condition")
    try:
        threshold = float(form_data.get("threshold"))
    except (TypeError, ValueError):
        return HTMLResponse(f"<div class='alert alert-danger'>{trans['invalid_threshold']}</div>")

    # 暂时只记录为“活动预警”
    details = f"{trans['alert_when']} {pair} {condition} {threshold}"
    exchange_service.add_history_record("warning", details)
    
    content = f"<div class='alert alert-info'>{trans['warning_set']}: {details}</div>"
    return HTMLResponse(content=content, headers={"HX-Trigger": "historyChanged"})

@app.get("/api/settle/history", response_class=HTMLResponse)
async def get_history_records(request: Request, filter_type: str = Query(None), lang: str = Depends(get_lang)):
    """
    获取用户的操作历史记录 HTML 片段。
    支持按类型筛选（如：计算记录、预警记录）。
    """
    trans = translations.get(lang, translations["zh"])
    records = exchange_service.get_history_records(filter_type)
    return templates.TemplateResponse("partials/history_list.html", {"request": request, "records": records, "trans": trans})

@app.post("/api/history/clear", response_class=HTMLResponse)
async def clear_history(request: Request, lang: str = Depends(get_lang)):
    """
    清空所有历史记录。
    """
    trans = translations.get(lang, translations["zh"])
    exchange_service.clear_history_records()
    response = templates.TemplateResponse("partials/history_list.html", {"request": request, "records": [], "trans": trans})
    response.headers["HX-Trigger"] = "historyChanged"
    return response
