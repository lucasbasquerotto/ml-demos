from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

browser = playwright.chromium.launch()
page = browser.new_page()
page.goto("https://playwright.dev/")
bytes = page.screenshot(path="example.png")
browser.close()

playwright.stop()

# save bytes as a image
with open("example.png", "wb") as f:
    f.write(bytes)