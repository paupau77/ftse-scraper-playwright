import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_lse_table(url, output_csv):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print(f"Opening {url}")
        await page.goto(url)

        # Aceptar cookies
        try:
            await page.click('button[aria-label="Accept cookies"]', timeout=5000)
            print("Cookies accepted")
            await page.wait_for_timeout(2000)
        except Exception:
            print("No cookie banner found or already accepted")

        # Esperar la tabla con el nuevo selector basado en el HTML
        await page.wait_for_selector("table.ftse-index-table-table tbody tr", timeout=60000)

        # Extraer filas de la tabla
        rows = await page.query_selector_all("table.ftse-index-table-table tbody tr")

        if not rows:
            print("No table rows found. Exiting.")
            await browser.close()
            return

        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Actualizamos los encabezados ya que 'Industry Classification' no está en el HTML actual
            writer.writerow(['Ticker Symbol', 'Company Name'])

            for row in rows:
                cols = await row.query_selector_all("td")
                if len(cols) >= 2: # Se aseguran de que haya al menos dos columnas
                    # 'Ticker Symbol' es la primera columna
                    ticker = (await cols[0].inner_text()).strip()
                    # 'Company Name' es la segunda columna
                    company_name = (await cols[1].inner_text()).strip()
                    writer.writerow([ticker, company_name])

        print(f"Data saved to {output_csv}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_lse_table(
        "https://www.londonstockexchange.com/indices/ftse-all-share/constituents/table",
        "ftse_all_share_playwright.csv"
    ))
    
    asyncio.run(scrape_lse_table(
        "https://www.londonstockexchange.com/indices/ftse-aim-all-share/constituents/table",
        "ftse_aim_all_share_playwright.csv"
    ))