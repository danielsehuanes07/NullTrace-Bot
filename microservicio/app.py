from fastapi import FastAPI
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import requests
import re
import asyncio
import httpx
from holehe.core import get_functions, import_submodules
import holehe.modules

app = FastAPI()

@app.get("/consultar/simit/{cedula}")
async def consultar_simit(cedula: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        resultado = {}

        async def interceptar(response):
            if "estadocuenta/consulta" in response.url:
                try:
                    data = await response.json()
                    resultado.update(data)
                except:
                    pass

        page.on("response", interceptar)
        await page.goto("https://fcm.org.co/simit/#/estado-cuenta",
            timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        inputs = await page.query_selector_all("input")
        for inp in inputs:
            placeholder = await inp.get_attribute("placeholder")
            if placeholder and any(word in placeholder.lower() for word in ["documento", "cédula", "identificación", "numero", "placa"]):
                await inp.fill(cedula)
                break
        await page.wait_for_timeout(500)
        await page.click("button[type='submit'], button.btn-search, .input-group button, input[type='submit']")
        for _ in range(20):
            if resultado:
                break
            await page.wait_for_timeout(500)
        await browser.close()
        if resultado:
            return resultado
        else:
            return {"error": "No se pudo obtener información"}


@app.get("/consultar/cedula/{cedula}")
async def consultar_cedula(cedula: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page_simit = await context.new_page()
        page_rues = await context.new_page()
        simit_resultado = {}
        rues_resultados = []

        async def interceptar(response):
            if "estadocuenta/consulta" in response.url:
                try:
                    data = await response.json()
                    simit_resultado.update(data)
                except:
                    pass

        page_simit.on("response", interceptar)

        # KEY FIX: return_exceptions=True hace que si el SIMIT falla,
        # el RUES sigue corriendo y retorna sus datos igual
        resultados_goto = await asyncio.gather(
            page_simit.goto("https://fcm.org.co/simit/#/estado-cuenta",
                timeout=60000, wait_until="domcontentloaded"),
            page_rues.goto(f"https://www.rues.org.co/buscar/RM/{cedula}",
                timeout=60000, wait_until="domcontentloaded"),
            return_exceptions=True
        )

        await asyncio.gather(
            page_simit.wait_for_timeout(5000),
            page_rues.wait_for_timeout(5000)
        )

        # SIMIT: solo intentar si la página cargó, con 2 reintentos
        simit_cargo = not isinstance(resultados_goto[0], Exception)
        if simit_cargo:
            for intento in range(2):
                try:
                    inputs = await page_simit.query_selector_all("input")
                    for inp in inputs:
                        placeholder = await inp.get_attribute("placeholder")
                        if placeholder and any(word in placeholder.lower() for word in ["documento", "cédula", "identificación", "numero", "placa"]):
                            await page_simit.fill(f"input[placeholder='{placeholder}']", cedula)
                            break
                    await page_simit.wait_for_timeout(500)
                    await page_simit.click("button[type='submit'], button.btn-search, .input-group button, input[type='submit']")
                    for _ in range(24):
                        if simit_resultado:
                            break
                        await page_simit.wait_for_timeout(500)
                    if simit_resultado:
                        break
                    # Si no llegó nada en el primer intento, recargar y reintentar
                    if intento == 0:
                        await page_simit.goto("https://fcm.org.co/simit/#/estado-cuenta",
                            timeout=60000, wait_until="domcontentloaded")
                        await page_simit.wait_for_timeout(5000)
                except Exception as e:
                    print(f"SIMIT intento {intento+1} falló: {e}")
                    break

        # RUES: independiente del SIMIT
        try:
            checkboxes = await page_rues.query_selector_all("input[type='checkbox']")
            for checkbox in checkboxes:
                is_checked = await checkbox.is_checked()
                if not is_checked:
                    await checkbox.click()
                    await page_rues.wait_for_timeout(300)
            await page_rues.click("button:has-text('Filtrar')")
            await page_rues.wait_for_timeout(3000)
            empresas = await page_rues.query_selector_all(".card-result, .result-item, [class*='result']")
            for empresa in empresas:
                texto = await empresa.inner_text()
                if texto.strip():
                    rues_resultados.append(texto.strip())
            if not rues_resultados:
                contenido = await page_rues.query_selector("main, #main, .container, #app")
                if contenido:
                    texto = await contenido.inner_text()
                    rues_resultados = [texto[:2000]]
        except Exception as e:
            print(f"RUES falló: {e}")

        await browser.close()

        return {
            "simit": simit_resultado if simit_resultado else {"error": "SIMIT no respondió — portal lento o caído"},
            "rues": {"cedula": cedula, "resultados": rues_resultados, "total": len(rues_resultados)}
        }


@app.get("/consultar/rues/{cedula}")
async def consultar_rues(cedula: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(f"https://www.rues.org.co/buscar/RM/{cedula}", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        checkboxes = await page.query_selector_all("input[type='checkbox']")
        for checkbox in checkboxes:
            is_checked = await checkbox.is_checked()
            if not is_checked:
                await checkbox.click()
                await page.wait_for_timeout(300)
        await page.click("button:has-text('Filtrar')")
        await page.wait_for_timeout(3000)
        resultados = []
        empresas = await page.query_selector_all(".card-result, .result-item, [class*='result']")
        for empresa in empresas:
            texto = await empresa.inner_text()
            if texto.strip():
                resultados.append(texto.strip())
        if not resultados:
            contenido = await page.query_selector("main, #main, .container, #app")
            if contenido:
                texto = await contenido.inner_text()
                resultados = [texto[:2000]]
        await browser.close()
        return {"cedula": cedula, "resultados": resultados, "total": len(resultados)}


@app.get("/consultar/negocio/{nombre}")
async def consultar_negocio(nombre: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(f"https://www.rues.org.co/buscar/RM/{nombre}", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        checkboxes = await page.query_selector_all("input[type='checkbox']")
        for checkbox in checkboxes:
            is_checked = await checkbox.is_checked()
            if not is_checked:
                await checkbox.click()
                await page.wait_for_timeout(300)
        await page.click("button:has-text('Filtrar')")
        await page.wait_for_timeout(3000)
        resultados = []
        empresas = await page.query_selector_all(".card-result, .result-item, [class*='result']")
        for empresa in empresas:
            texto = await empresa.inner_text()
            if texto.strip():
                resultados.append(texto.strip())
        if not resultados:
            contenido = await page.query_selector("main, #main, .container, #app")
            if contenido:
                texto = await contenido.inner_text()
                resultados = [texto[:3000]]
        await browser.close()
        return {"nombre": nombre, "resultados": resultados, "total": len(resultados)}


@app.get("/consultar/spam/{numero}")
async def consultar_spam(numero: str):
    numero_completo = numero if numero.startswith('+57') else f"+57{numero}"
    url = f"https://www.telguarder.com/co/tel/{numero_completo}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    multas_divs = soup.find_all("div", class_="ai-row-info-value")
    valores = [d.get_text(strip=True) for d in multas_divs]
    seguridad = soup.find("div", id="securityLevelValue")
    if seguridad:
        nivel_num = seguridad.get("data-security-level", "0")
        nivel = f"{nivel_num}%" if nivel_num != "0" else "Sin datos suficientes"
    else:
        nivel = "Sin datos suficientes"
    row3 = soup.find("div", class_="ai-row-3")
    texto_completo = row3.get_text(strip=True) if row3 else "Sin información"
    descripcion = texto_completo.split('Comparte')[0].strip()
    return {"numero": numero_completo, "valores": valores, "nivel_seguridad": nivel, "descripcion": descripcion}


@app.get("/screenshot/spam/{numero}")
async def screenshot_spam(numero: str):
    numero_completo = numero if numero.startswith('+57') else f"+57{numero}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(f"https://www.telguarder.com/co/tel/{numero_completo}", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="/tmp/spam.png")
        await browser.close()
        return {"ok": "screenshot guardado"}


@app.get("/screenshot/rues/{cedula}")
async def screenshot_rues(cedula: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = await context.new_page()
        await page.goto(f"https://www.rues.org.co/buscar/RM/{cedula}", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        checkboxes = await page.query_selector_all("input[type='checkbox']")
        for checkbox in checkboxes:
            is_checked = await checkbox.is_checked()
            if not is_checked:
                await checkbox.click()
                await page.wait_for_timeout(300)
        await page.click("button:has-text('Filtrar')")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="/tmp/rues.png")
        await browser.close()
        return {"ok": "screenshot guardado"}


@app.get("/consultar/email/{correo}")
async def consultar_email(correo: str):
    """
    Verifica en qué plataformas/redes sociales está registrado un correo.
    Consulta ~121 sitios en paralelo sin necesitar credenciales.
    """
    # Carga dinámica de todos los módulos de holehe (twitter, instagram, github, etc.)
    mods = import_submodules(holehe.modules)
    funcs = get_functions(mods)

    out = []  # Lista compartida — cada módulo hace append() con su resultado

    async with httpx.AsyncClient() as client:
        # Lanzamos los 121 módulos en paralelo
        tasks = [func(correo, client, out) for func in funcs]
        await asyncio.gather(*tasks, return_exceptions=True)
        # return_exceptions=True → si un módulo falla, los demás siguen corriendo

    # Separamos en 3 categorías según lo que devuelve cada módulo
    encontrados    = [r["name"] for r in out if r.get("exists") is True]
    no_encontrados = [r["name"] for r in out if r.get("exists") is False and not r.get("rateLimit")]
    rate_limited   = [r["name"] for r in out if r.get("rateLimit")]

    return {
        "correo": correo,
        "total_encontrados": len(encontrados),
        "registrado_en": encontrados,       # ← lo que le mandamos al bot
        "no_registrado_en": no_encontrados,
        "rate_limited": rate_limited,       # sitios que bloquearon la consulta
    }
