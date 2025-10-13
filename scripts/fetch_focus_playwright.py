from playwright.sync_api import sync_playwright
import sys

url = 'https://www.focus.pl/artykul/skamienialosc-gad-sprzed-242-milionow-lat'
out_path = 'logs/focuspl_raw.html'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, timeout=30000)
    content = page.content()
    browser.close()

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(content)

# print a short snippet to console
print(content[:8000])
print('\n--- Saved rendered HTML to', out_path, '---')
