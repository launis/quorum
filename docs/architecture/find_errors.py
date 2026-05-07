from playwright.sync_api import sync_playwright
import os

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f'file:///{os.path.abspath("full_test.html").replace(os.sep, "/")}')
    page.wait_for_timeout(2000)
    errors = page.locator('svg text:has-text("Syntax error")').all()
    print([e.evaluate('el => el.closest(".mermaid").id') for e in errors])
    browser.close()
