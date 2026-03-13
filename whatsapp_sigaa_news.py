import datetime
import os
from datetime import date
import asyncio
from telegram import Bot

USERNAME = os.getenv("SIGAA_USERNAME")
PASSWORD = os.getenv("SIGAA_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")
TODAY = date.today()



async def send_to_telegram(news) :
    if(len(news) == 0):
        print("Nenhuma notícia lançada hoje nas suas turmas!")
    else:
        for new in news:
            await send_message(format_news_message(new["title"], new["content"], new["class"]))
async def send_message(message):
    async with Bot(TELEGRAM_BOT_TOKEN) as bot:
        await bot.send_message(chat_id=TELEGRAM_USER_ID, text=message, parse_mode="HTML")
    

def news_date_is_today(date_string):
    date = datetime.datetime.strptime(date_string, "%d/%m/%Y").date()
    return date == TODAY

def format_news_message(news_title, news_content, news_class):
    return f"<i>{news_class}</i>\n<b>{news_title}</b>\n\n{news_content}"


from playwright.sync_api import sync_playwright
def generate_authenticated_state(browser):
    context = browser.new_context()
    page = context.new_page()
    
    page.goto("https://autenticacao.ufrn.br")
    page.wait_for_load_state()
    
    page.locator("#username").fill(USERNAME)
    page.locator("#password").fill(PASSWORD)
    page.get_by_role("button", name="Entrar").click()
    context.storage_state(path="state.json")

    context.close()
    
def login(page):
    page.goto("https://sigaa.ufrn.br")
    page.get_by_role("link", name="Login").click()
    page.wait_for_load_state()
    
with sync_playwright() as p:
    
    browser = p.chromium.launch(
        args=[
            "--start-maximized",
            "--window-size=12800,720",
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-extensions"
        ]
    )

    if not os.path.isfile("state.json"):
        generate_authenticated_state(browser)
        

    
    context = browser.new_context(storage_state="state.json")
    page = context.new_page()
    
    if "autenticacao" in page.url:
        os.remove("state.json")
        generate_authenticated_state(browser)
    
    login(page)
    news = []
    
    for subject in page.locator("td.descricao").all():
        class_name = subject.inner_text()
        subject.locator("a").click()
        page.wait_for_load_state()
        page.locator(".itemMenu").nth(6).click()
        page.wait_for_load_state()
        data_noticia = page.locator(".width75").first.inner_text()
        if not news_date_is_today(data_noticia):
            page.go_back()
            page.go_back()
            page.wait_for_load_state()
            continue
        page.locator(".icon>a").first.click()
        news_title = page.locator('label:text("Título:") + span').inner_text()
        news_content = page.locator(".conteudoNoticia").inner_text().replace("\xa0", " ").strip()
        news.append({
            "class": class_name,
            "title": news_title,
            "content": news_content
        })
        page.go_back()
        page.go_back()
        page.go_back()
        page.wait_for_load_state()
        

asyncio.run(send_to_telegram(news))
    
     
    