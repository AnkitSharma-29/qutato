import os
import asyncio
from playwright.async_api import async_playwright
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def main():
    print("🚀 Launching local Brave browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            headless=False
        )
        page = await browser.new_page()
        
        print("🌐 Navigating to greatinflux.com...")
        await page.goto("https://greatinflux.com/")
        await page.wait_for_load_state("domcontentloaded")
        
        print("🕵️ Extracting page text...")
        home_text = await page.locator("body").inner_text()
        
        print("🌐 Navigating to 'About Us'...")
        try:
            await page.goto("https://greatinflux.com/about-us/", timeout=15000)
            await page.wait_for_load_state("domcontentloaded")
            about_text = await page.locator("body").inner_text()
        except:
            about_text = ""
            
        full_text = home_text + "\n\n" + about_text
        
        await browser.close()
        
    print("🧠 Asking LLM to find the owner/founder name...")
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not set.")
        return
    
    llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    
    prompt = f"Based on the following scraped text from greatinflux.com, who is the owner, founder, or CEO? Only reply with the name, or say 'Not Found' if it's missing.\n\n{full_text[:15000]}"
    
    result = await llm.ainvoke([HumanMessage(content=prompt)])
    
    print("\n📦 Mission Complete")
    print("-------------------")
    print("OWNER:", result.content)

if __name__ == "__main__":
    asyncio.run(main())
