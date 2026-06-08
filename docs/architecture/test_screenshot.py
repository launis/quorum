import os

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    file_path = f"file:///{os.path.abspath('test_mermaid.html').replace(os.sep, '/')}"
    page.goto(file_path, wait_until='networkidle')
    page.wait_for_timeout(2000)

    # Take screenshot of the first error
    error_el = page.locator('svg[id^="mermaid-"] text:has-text("Syntax error")').first
    if error_el.count() > 0:
        error_el.evaluate("el => el.closest('.mermaid').scrollIntoView()")
        page.wait_for_timeout(500)
        page.screenshot(path="mermaid_test.png")
    else:
        print("No syntax error found in SVG")
        page.screenshot(path="mermaid_test.png", full_page=True)
    browser.close()
