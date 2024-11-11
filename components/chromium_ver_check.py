from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    browser_version = browser.version
    print(f"Chromium version: {browser_version}")
    browser.close()