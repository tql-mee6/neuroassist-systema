import asyncio, urllib.request
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width":1280,"height":760})
        await pg.goto("http://localhost:8765"); await pg.wait_for_timeout(1500)
        await pg.screenshot(path="docs/ui_idle.png")
        urllib.request.urlopen("http://localhost:8765/demo")
        shot=0
        for i in range(100):
            await pg.wait_for_timeout(1000)
            t = await pg.inner_text("#text")
            if shot==0 and len(t.strip())>=3:
                await pg.screenshot(path="docs/ui_typing.png"); shot=1
            if t.replace("↵","").strip().startswith("привет"):
                await pg.wait_for_timeout(600); await pg.screenshot(path="docs/ui_done.png"); break
        await b.close()
asyncio.run(main())
