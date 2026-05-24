import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

TICKERS = {
    "SPY":  ("https://www.acuantoesta.com.ar/cedears", "SPY"),
    "MSFT": ("https://www.acuantoesta.com.ar/cedears", "MSFT"),
    "NU":   ("https://www.acuantoesta.com.ar/cedears", "NU"),
    "TSM":  ("https://www.acuantoesta.com.ar/cedears", "TSM"),
}

def extraer_precio(page, ticker):
    try:
        # Espera a que cargue la tabla
        page.wait_for_selector("table", timeout=15000)
        # Busca la fila que contiene el ticker
        rows = page.query_selector_all("tr")
        for row in rows:
            text = row.inner_text()
            if re.search(rf'\b{ticker}\b', text, re.IGNORECASE):
                # Busca números con decimales en la fila
                numeros = re.findall(r'\d+[.,]\d+', text)
                for n in numeros:
                    val = float(n.replace(',', '.'))
                    if 0.5 < val < 50000:  # rango razonable para precio USD
                        return val
    except Exception as e:
        print(f"Error con {ticker}: {e}")
    return None

def main():
    precios = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Carga la página de CEDEARs una sola vez
        print("Cargando acuantoesta.com.ar/cedears...")
        page.goto("https://www.acuantoesta.com.ar/cedears", wait_until="networkidle")
        
        for ticker, (url, symbol) in TICKERS.items():
            print(f"Buscando {ticker}...")
            precio = extraer_precio(page, symbol)
            precios[ticker] = precio
            print(f"  {ticker}: {precio}")
        
        browser.close()
    
    precios["actualizado"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    with open("precios.json", "w") as f:
        json.dump(precios, f, indent=2)
    
    print("precios.json actualizado:", precios)

if __name__ == "__main__":
    main()
