import os
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WhatsAppSender:

    def __init__(self):

        chrome_options = Options()

        profile_path = os.path.abspath("chrome-data")

        if not os.path.exists(profile_path):
            os.makedirs(profile_path)

        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 40)

        print("Abriendo WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")

        self.wait.until(
            EC.presence_of_element_located((By.ID, "side"))
        )

        print("WhatsApp listo")

    def enviar_mensaje(self, numero, mensaje):

        try:
            mensaje_encoded = urllib.parse.quote(mensaje)

            url = f"https://web.whatsapp.com/send?phone=57{numero}&text={mensaje_encoded}"
            self.driver.get(url)

            # Esperar la caja editable
            caja = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"]')
                )
            )

            # Forzar foco
            caja.click()

            time.sleep(1)

            # Enviar con ENTER
            caja.send_keys(Keys.ENTER)

            print(f"Mensaje enviado a {numero}")

        except Exception as e:
            print("Error enviando mensaje:", e)

    def cerrar(self):
        self.driver.quit()
        print("Navegador cerrado")