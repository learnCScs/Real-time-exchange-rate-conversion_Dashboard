from fastapi import FastAPI, Request, Form, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.exchange_api import exchange_service
import os

app = FastAPI(title="Exchange Rate Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Common currencies for dropdowns
CURRENCIES = ["USD", "CNY", "EUR", "GBP", "JPY", "HKD", "AUD", "CAD", "SGD", "CHF", "INR", "RUB", "KRW", "THB", "VND", "MYR", "IDR", "PHP", "TWD", "NZD"]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "currencies": CURRENCIES})

@app.get("/api/realtime", response_class=HTMLResponse)
async def get_realtime_rates(request: Request):
    rates = await exchange_service.get_realtime_rates()
    # Filter for main currencies to display
    display_rates = {k: v for k, v in rates.items() if k in CURRENCIES}
    return templates.TemplateResponse("partials/rates_table.html", {"request": request, "rates": display_rates})

@app.post("/api/convert", response_class=HTMLResponse)
async def convert_currency(request: Request, amount: float = Form(...), from_curr: str = Form(...), to_curr: str = Form(...)):
    rates = await exchange_service.get_realtime_rates()
    result = exchange_service.convert_currency(amount, from_curr, to_curr, rates)
    return f"<div class='alert alert-success mt-3'>Result: {amount} {from_curr} = <strong>{result} {to_curr}</strong></div>"

@app.get("/api/news", response_class=HTMLResponse)
async def get_news(request: Request):
    news = await exchange_service.get_news()
    return templates.TemplateResponse("partials/news_list.html", {"request": request, "news": news})

@app.get("/api/history")
async def get_history(base: str = Query("USD"), target: str = Query("CNY"), days: int = Query(30)):
    data = await exchange_service.get_historical_data(base, target, days)
    return JSONResponse(content=data)

@app.post("/api/purchase/cost", response_class=HTMLResponse)
async def calculate_purchase_cost(request: Request):
    # Note: FastAPI Form list handling might need specific frontend naming like amounts&amounts
    # For simplicity in HTMX, we might receive them differently or parse form data manually if complex.
    # Let's assume simple single item calculation or handle list if possible.
    # Actually, for a dynamic list, it's easier to accept a JSON body or parse raw form.
    # But HTMX sends form data. Let's simplify: User adds rows, submits form.
    # We will read form data directly from request for dynamic fields.
    form_data = await request.form()
    
    items = []
    rates = await exchange_service.get_realtime_rates()
    cny_rate = rates.get("CNY", 1.0) # Assuming we want cost in CNY
    
    # Extract lists manually since keys might be 'amount' and 'currency' repeated
    raw_amounts = form_data.getlist("amount")
    raw_currencies = form_data.getlist("currency")
    
    total_cny = 0
    results = []
    
    for amt, curr in zip(raw_amounts, raw_currencies):
        try:
            val = float(amt)
            # Convert to USD then to CNY
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
            
    # Find best (lowest cost) - wait, this logic assumes comparing OPTIONS for the SAME item?
    # Or summing up a BOM? The prompt says "Compare multiple supplier quotes... highlight lowest".
    # So it's options.
    
    if results:
        min_cost = min(r["cny_cost"] for r in results)
        for r in results:
            r["is_best"] = (r["cny_cost"] == min_cost)
            
    # Log to history
    exchange_service.add_history_record("purchase", {"total_options": len(results), "best_price_cny": min_cost if results else 0})

    return templates.TemplateResponse("partials/purchase_result.html", {"request": request, "results": results})

@app.post("/api/sale/price", response_class=HTMLResponse)
async def calculate_sale_price(request: Request):
    # Similar handling for lists
    form_data = await request.form()
    
    try:
        cost_cny = float(form_data.get("cost_cny", 0))
    except ValueError:
        return HTMLResponse("<div class='alert alert-danger'>Invalid Cost</div>")

    raw_markets = form_data.getlist("market") # e.g. USD, EUR
    raw_margins = form_data.getlist("margin") # e.g. 20 for 20%
    
    rates = await exchange_service.get_realtime_rates()
    cny_rate = rates.get("CNY", 1.0)
    
    results = []
    for mkt, margin in zip(raw_markets, raw_margins):
        try:
            margin_pct = float(margin) / 100.0
            target_price_cny = cost_cny * (1 + margin_pct)
            
            # Convert CNY -> USD -> Target Market Currency
            # CNY -> USD
            price_usd = target_price_cny / cny_rate
            # USD -> Target
            price_local = price_usd * rates.get(mkt, 1.0)
            
            results.append({
                "market": mkt,
                "margin": margin,
                "price_local": round(price_local, 2),
                "price_cny": round(target_price_cny, 2)
            })
        except:
            continue
            
    exchange_service.add_history_record("sale", {"cost_cny": cost_cny, "markets_count": len(results)})
    
    return templates.TemplateResponse("partials/sale_result.html", {"request": request, "results": results})

@app.post("/api/warning/add", response_class=HTMLResponse)
async def add_warning(request: Request):
    form_data = await request.form()
    pair = form_data.get("pair")
    condition = form_data.get("condition")
    try:
        threshold = float(form_data.get("threshold"))
    except (TypeError, ValueError):
        return HTMLResponse("<div class='alert alert-danger'>Invalid Threshold</div>")

    # Just log it for now as "Active Warning"
    details = f"Alert when {pair} {condition} {threshold}"
    exchange_service.add_history_record("warning", details)
    return f"<div class='alert alert-info'>Warning set: {details}</div>"

@app.get("/api/settle/history", response_class=HTMLResponse)
async def get_history_records(request: Request, filter_type: str = Query(None)):
    records = exchange_service.get_history_records(filter_type)
    return templates.TemplateResponse("partials/history_list.html", {"request": request, "records": records})
