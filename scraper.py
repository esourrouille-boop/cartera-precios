import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

TICKERS = ["SPY", "MSFT", "NU", "TSM"]

def extraer_precios(page):
    """
    Extrae precios USD de la tabla de acuantoesta.
    La tabla tiene columnas: Ticker | Precio ARS | Cambio ARS | Precio USD | Cambio USD | Tipo de Cambio
    Precio USD es la 4ta columna (índice 3).
    """
    precios = {}
    try:
        page.wait_for_selector("table tbody tr", timeout=20000)
        rows = page.query_selector_all("table tbody tr")
        
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) < 4:
                continue
            
            ticker_text = cells[0].inner_text().strip().upper()
            
            # Verificar si esta fila corresponde a alguno de nuestros tickers
            for ticker in TICKERS:
                if ticker_text == ticker:
                    precio_usd_text = cells[3].inner_text().strip()
                    # Limpiar: quitar "US$", espacios, y convertir coma decimal a punto
                    precio_usd_text = precio_usd_text.replace("US$", "").strip()
                    precio_usd_text = precio_usd_text.replace(".", "").replace(",", ".")
                    try:
                        valor = float(precio_usd_text)
                        if valor > 0:
                            precios[ticker] = valor
                            print(f"  {ticker}: USD {valor}")
                    except ValueError:
                        print(f"  {ticker}: no se pudo parsear '{precio_usd_text}'")
    except Exception as e:
        print(f"Error extrayendo precios: {e}")
    
    return precios

def main():
    precios = {t: None for t in TICKERS}
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        print("Cargando acuantoesta.com.ar/cedears...")
        page.goto("https://www.acuantoesta.com.ar/cedears", wait_until="networkidle", timeout=30000)
        
        # Espera extra para asegurarse que el JS terminó de renderizar
        page.wait_for_timeout(3000)
        
        encontrados = extraer_precios(page)
        precios.update(encontrados)
        
        browser.close()
    
    precios["actualizado"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    with open("precios.json", "w") as f:
        json.dump(precios, f, indent=2)
    
    print("\nprecios.json guardado:")
    print(json.dumps(precios, indent=2))

if __name__ == "__main__":
    main()
