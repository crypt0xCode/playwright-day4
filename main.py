import asyncio

from playwright.async_api import async_playwright, expect
from anticaptchaofficial.recaptchav2enterpriseproxyless import *
from data import *


async def get_profile_data(profile_id: str) -> dict:
    """Запрашивает и возвращает данные профиля в виде словаря."""
    response = requests.get(adspower_api_url, params={
        "user_id": profile_id
    })
    data = response.json()
    print(data)

    if data["code"] != 0:
        raise Exception(f"Не удалось получить данные профиля: {data['msg']}")

    return data


async def main():
    async with async_playwright() as p:
        profile_data = await get_profile_data(profile_id=profile_id)

        browser = await p.chromium.connect_over_cdp(profile_data['data']['ws']['puppeteer'],
                                                    slow_mo=2000,
                                                    )

        solver = recaptchaV2EnterpriseProxyless()
        solver.set_verbose(1)
        solver.set_key(API_KEY)
        solver.set_website_url('https://app.getgrass.io/register')
        solver.set_website_key("6LeeT-0pAAAAAFJ5JnCpNcbYCBcAerNHlkK4nm6y")

        g_response = solver.solve_and_return_solution()
        if g_response != 0:
            print("g-response: " + g_response)
        else:
            print("task finished with error " + solver.error_code)

        context = browser.contexts[0]
        page = await context.new_page()
        await page.goto('https://app.getgrass.io/register')
        await page.wait_for_load_state()
        await asyncio.sleep(3)

        # Click cookies button.
        btn_cookies = page.locator('//*[@id="chakra-modal--body-:r4:"]/div/div/button[1]')
        if not await btn_cookies.is_hidden():
            await btn_cookies.click()
            await asyncio.sleep(3)

        # Enter captcha.
        result = await page.evaluate(
            f"""() => window.___grecaptcha_cfg.clients['0']['S']['S']['callback']('{g_response}')"""
        )
        print(result)

        # Fill e-mail.
        email_form = page.locator('//*[@id="field-:r5:"]')
        await email_form.fill(EMAIL)
        await asyncio.sleep(3)

        # Fill password.
        password_form = page.locator('//*[@id="field-:r6:"]')
        await password_form.fill(PASSWORD)
        await asyncio.sleep(3)

        # Repeat password.
        password_form = page.locator('//*[@id="field-:r7:"]')
        await password_form.fill(PASSWORD)
        await asyncio.sleep(3)

        # Agree with Terms.
        checkbox = page.locator('body > div.css-t1k2od > div > div.css-0 > div > div.css-10heyz4 > div > div.css-0 > div > div.chakra-stack.css-1811skr > form > div > div:nth-child(5) > label > span.chakra-checkbox__control.css-i88593')
        await checkbox.click()
        await asyncio.sleep(3)

        await page.wait_for_function("window.___grecaptcha_cfg !== undefined")

        # Click Register.
        await page.wait_for_selector('body > div.css-t1k2od > div > div.css-0 > div > div.css-10heyz4 > div > div.css-0 > div > div.chakra-stack.css-1811skr > form > button', state="attached")
        register = page.locator('body > div.css-t1k2od > div > div.css-0 > div > div.css-10heyz4 > div > div.css-0 > div > div.chakra-stack.css-1811skr > form > button')
        await register.click()
        await asyncio.sleep(3)

        await context.close()

if __name__ == '__main__':
    asyncio.run(main())
