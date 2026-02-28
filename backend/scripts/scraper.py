import asyncio
import json
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
from crawlee.browsers import BrowserPool, PlaywrightBrowserController, PlaywrightBrowserPlugin

# Tuodaan Crawlee-kehyksen työkalut (v1.0+)
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext

# Camoufox on asennettava erikseen: uv pip install camoufox[geoip]
try:
    from typing import override

    from camoufox import AsyncNewBrowser

    class CamoufoxPlugin(PlaywrightBrowserPlugin):
        @override
        async def new_browser(self) -> PlaywrightBrowserController:
            if not self._playwright:
                raise RuntimeError('Playwright plugin error.')
            options = self._browser_launch_options.copy()
            options["headless"] = False # Gemini requires headful for full rendering
            return PlaywrightBrowserController(
                browser=await AsyncNewBrowser(self._playwright, **options),
                max_open_pages_per_browser=1,
                header_generator=None,
            )
    HAS_CAMOUFOX = True
except ImportError:
    HAS_CAMOUFOX = False

async def main():
    # ---------------------------------------------------------
    # 1. SYÖTTEET JA RAJAUKSET (KYSYTÄÄN KÄYTTÄJÄLTÄ)
    # ---------------------------------------------------------
    user_url = input("Syötä jaetun keskustelun URL-osoite: ").strip()

    if not user_url:
        print("⚠️ Osoite puuttuu. Lopetetaan.")
        return

    urls_to_scrape = [user_url]

    # Alustan tunnistus
    provider = None
    if "chatgpt.com/share/" in user_url or "chat.openai.com/share/" in user_url:
        provider = "chatgpt"
        print("🔍 Tunnistettiin alustaksi: ChatGPT")
    elif "gemini.google.com/share/" in user_url:
        provider = "gemini"
        print("🔍 Tunnistettiin alustaksi: Gemini")
    else:
        print("⚠️ Alustaa ei tunnistettu automaattisesti URL-osoitteesta.")
        while True:
            provider_input = input("Valitse alusta (1 = ChatGPT, 2 = Gemini): ").strip()
            if provider_input == '1':
                provider = "chatgpt"
                break
            elif provider_input == '2':
                provider = "gemini"
                break
            print("Virheellinen valinta, yritä uudelleen.")

    # Keskusmuisti datan tallennukseen tiedostovientejä varten
    scraped_data = []

    # ---------------------------------------------------------
    # 2. RYÖMIJÄN (CRAWLER) ALUSTUS
    # ---------------------------------------------------------
    # Crawlee hoitaa botin kierron (anti-fingerprinting), jonotuksen ja rinnakkaisuuden.
    # Käynnistetään PlaywrightCrawler headless-tilassa, paitsi jos Geminillä (jonka pitää näyttää botin estot)
    crawler_kwargs_base = {
        "max_requests_per_crawl": 10,
    }

    # Valitaan ryömijälle sopivat asetukset / ohitukset käytetyn alustan perusteella
    if provider == "gemini" and HAS_CAMOUFOX:
        print("🛡️ Käytetään Camoufoxia Geminin botin estoja vastaan...")
        crawler = PlaywrightCrawler(
            **crawler_kwargs_base,
            browser_pool=BrowserPool(plugins=[CamoufoxPlugin()]),
        )
    else:
        # Vakio headless selain ChatGPT:lle
        crawler = PlaywrightCrawler(
            **crawler_kwargs_base,
            headless=True,
            browser_type='chromium'
        )

    # ---------------------------------------------------------
    # 3. KÄSITTELIJÄ JA DATAN POIMINTA (ROUTER)
    # ---------------------------------------------------------
    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlingContext) -> None:
        url = context.request.url
        context.log.info(f"Käsitellään URL: {url}")

        page = context.page
        conversation = []

        try:
            # --- CHATGPT ---
            if provider == "chatgpt":
                # Odotetaan sivun pääsisällön latautumista (Playwright odottaa selektoria)
                await page.wait_for_selector('[data-message-author-role]', timeout=15000)

                # Etsitään kaikki viestiblokit asynkronisesti
                messages = await page.locator('[data-message-author-role]').all()

                for order, msg in enumerate(messages, start=1):
                    # Tunnistetaan rooli attribuutin perusteella (user tai assistant)
                    role_attr = await msg.get_attribute('data-message-author-role')
                    role = "User" if role_attr == "user" else "AI"

                    # Poimitaan pelkkä teksti
                    text = await msg.inner_text()
                    if text.strip():
                        conversation.append({
                            "order": order,
                            "role": role,
                            "text": text.strip()
                        })

            # --- GEMINI ---
            elif provider == "gemini":
                # Geminin käyttöliittymä on raskaampi ja voi kysyä evästeitä.
                try:
                    # Yritetään klikata "Accept all" / "Hyväksy kaikki"
                    await page.wait_for_timeout(3000)
                    btn = page.locator('button:has-text("Accept all"), button:has-text("Hyväksy kaikki"), button:has-text("Hyväksy")').first
                    if await btn.count() > 0:
                        context.log.info("Löydettiin evästekysely pääikkunasta, hyväksytään...")
                        await btn.click()
                    else:
                        for frame in page.frames:
                            fbtn = frame.locator('button:has-text("Accept all"), button:has-text("Hyväksy kaikki"), button:has-text("Hyväksy")').first
                            if await fbtn.count() > 0:
                                context.log.info("Löydettiin evästekysely iframesta, hyväksytään...")
                                await fbtn.click()
                                break
                    await page.wait_for_timeout(3000)
                except Exception as e:
                    context.log.debug(f"Evästeiden hyväksyntää ei tarvittu tai se epäonnistui: {e}")

                # Odotetaan itse chatin latautumista.
                # Käytetään joustavampaa odotusta elementeille
                try:
                    # Gemini käyttää viesteissä yleensä nimistä pääteltäviä elementtejä tai div-luokkia
                    await page.wait_for_selector('message-content, user-query-container, model-response-container, [class*="message"], [class*="query"]', timeout=30000)
                except Exception:
                    context.log.warning("Tiettyjä chat-selektoreita ei löytynyt, jatketaan sivun lukemista silti.")

                # Käytetään BeautifulSoup 4:ää monimutkaisemman ja vaihtelevan DOM-puun jäsennelyyn
                html = await page.content()
                soup = BeautifulSoup(html, 'html.parser')
                # Geminin DOM-luokat vaihtelevat usein. ETSITÄÄN joko viralliset container-tagit tai heuristiikka
                blocks = soup.find_all(['message-content', 'user-query-container', 'model-response-container', 'div'])

                order = 1
                seen_texts = set() # Estetään saman sisällön toistuminকালীন Geminin sisäkkäisistä elementeistä

                for block in blocks:
                    tag_name = block.name.lower()
                    classes = " ".join(block.get('class', [])).lower()

                    # Tarkistetaan onko tämä chatin lohko iteratiivisesti
                    is_chat_block = False
                    role = None

                    if tag_name == 'user-query-container' or 'user-query' in classes:
                        is_chat_block = True
                        role = "User"
                    elif tag_name == 'model-response-container' or 'model-response' in classes:
                        is_chat_block = True
                        role = "AI"
                    # Vanha heuristiikka varalle
                    elif tag_name == 'message-content' or ('query' in classes or 'response' in classes or 'message' in classes):
                        text = block.get_text(strip=True)
                        if len(text) > 20: # skip small buttons
                            is_chat_block = True
                            if "user" in classes or "query" in classes or "user" in tag_name:
                                role = "User"
                            elif "model" in classes or "response" in classes or "ai" in classes:
                                role = "AI"

                    if is_chat_block and role:
                        text = block.get_text(separator='\n', strip=True)
                        if text:
                            # Tarkistetaan ettei ole mennyt vahingossa liikaa ylimääräisiä luokkia (esim. koko sivu)
                            # Tarkistetaan myös ettei olla jo lisätty samaa tekstiä (DOM:n sisäkkäisyysongelma)
                            if len(text) < 5000 and text not in seen_texts:
                                seen_texts.add(text)
                                conversation.append({
                                    "order": order,
                                    "role": role,
                                    "text": text
                                })
                                order += 1
            else:
                context.log.warning(f"Tuntematon alusta tai väärä linkki: {url}")
                return

            # --- TALLENNUS JA VIRHEENHALLINTA ---
            if conversation:
                # Luodaan haluttu tietorakenne
                data_item = {
                    "url": url,
                    # Tallenetaan muotoon YYYY-MM-DDTHH:MM:SS
                    "scraped_at": datetime.now().replace(microsecond=0).isoformat(),
                    "conversation": conversation
                }

                # Pushataan Crawleen sisäiseen Dataset-varastoon (varmuuskopio)
                await context.push_data(data_item)

                # Lisätään keskusmuistiin JSON/Excel-vientiä varten
                scraped_data.append(data_item)
                context.log.info(f"✅ Onnistui: Löydettiin {len(conversation)} viestiä sivulta {url}")
            else:
                context.log.warning(f"⚠️ Sivulta ei löytynyt viestejä. DOM-rakenne saattaa olla muuttunut: {url}")

        except Exception as e:
            # Virheenhallinta: Jos sivusto antaa 404 tai Timeoutin, kaapataan virhe.
            # Nostamalla poikkeuksen (raise) Crawlee asettaa osoitteen takaisin jonoon ja yrittää uudelleen.
            context.log.error(f"❌ Virhe käsiteltäessä sivua {url}: {e}")
            raise e

    # ---------------------------------------------------------
    # 4. SUORITUSLOGIIKKA
    # ---------------------------------------------------------
    print(f"🚀 Käynnistetään ryömijä {len(urls_to_scrape)} linkille...")
    await crawler.run(urls_to_scrape)

    # ---------------------------------------------------------
    # 5. TIETOMALLI JA TULOSTEET (EXPORT)
    # ---------------------------------------------------------
    if scraped_data:
        # Vaihtoehto A: JSON-muoto (Hierarkkinen)
        json_filename = "ai_chats_scraped.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)
        print(f"\n📄 Data tallennettu hierarkkisessa JSON-muodossa: {json_filename}")

        # Vaihtoehto B: Pandas Excel-vienti (Litteä / Flattened muoto analyysiin)
        excel_filename = "ai_chats_scraped.xlsx"
        flat_data = []
        for chat in scraped_data:
            for msg in chat["conversation"]:
                flat_data.append({
                    "URL": chat["url"],
                    "Scraped_At": chat["scraped_at"],
                    "Order": msg["order"],
                    "Role": msg["role"],
                    "Text": msg["text"]
                })

        try:
            df = pd.DataFrame(flat_data)
            df.to_excel(excel_filename, index=False, engine='openpyxl')
            print(f"📊 Data tallennettu litteässä Excel-muodossa: {excel_filename}")
        except Exception as e:
            print(f"❌ Virhe Excel-viennissä: {e}")
    else:
        print("\n⚠️ Ei tallennettavaa dataa. Tarkista linkit ja lokitiedot.")

if __name__ == "__main__":
    # Käynnistetään PlaywrightCrawleria pyörittävä tapahtumasilmukka
    asyncio.run(main())
