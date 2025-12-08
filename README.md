# Exchange Rate Dashboard

A lightweight, full-featured exchange rate dashboard using Python (FastAPI), HTML/CSS/HTMX, and Chart.js.

## Features
- **Real-time Rates**: Updates every 5 minutes (cached).
- **Currency Converter**: Instant conversion.
- **Market News**: Latest forex news.
- **Visualization**: Historical trends and volatility radar.
- **Tools**: Purchase cost comparison and smart pricing calculator.
- **History**: Logs of all calculations and alerts.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    - Rename `.env.example` to `.env`.
    - Add your API keys:
        - [ExchangeRate-API](https://www.exchangerate-api.com/) (Free)
        - [Alpha Vantage](https://www.alphavantage.co/) (Free)

3.  **Run the Application**:
    ```bash
    uvicorn app.main:app --reload
    ```

4.  **Access**:
    Open your browser and go to `http://127.0.0.1:8000`.

## Project Structure
- `app/`: Backend code (FastAPI).
- `templates/`: HTML templates (Jinja2).
- `static/`: CSS and JS files.
- `data/`: JSON files for data persistence.
