import logging
import re
import sys
import time

import requests
from pyvirtualdisplay import Display
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import chromedriver_autoinstaller

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

display = Display(visible=0, size=(800, 800))
display.start()

logging.basicConfig(
    filename="token_update.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
# and if it doesn't exist, download it automatically,
# then add chromedriver to path

logging.getLogger("seleniumwire").setLevel(logging.WARNING)

def send_email(subject, body):
    from_email = sys.argv[4]
    from_pwd = sys.argv[5]
    to_email = sys.argv[6]

    # 设置邮件内容
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    # 使用 QQ 邮箱 SMTP 服务发送邮件
    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:  # QQ 邮箱需要使用 SSL 连接
            server.login(from_email, from_pwd)
            server.sendmail(from_email, to_email, msg.as_string())
            logging.info("Email sented.")
    except:
        pass


def update_token():
    """
    This function automates the login to the IELTS results service website, retrieves the authentication token from the URL, and updates the token by sending it to a specified API endpoint.
    Steps performed by the function:
    1. Initialize Chrome WebDriver with specific options to run in headless mode and suppress logs.
    2. Open the IELTS results service website.
    3. Enter email and password to log in.
    4. Click the submit button to log in.
    5. Wait for the URL to contain the authentication token.
    6. Extract the token from the URL.
    7. Send the token to the specified API endpoint for updating.
    8. Print the status of the token update operation.
    Note:
    - Ensure 'chromedriver.exe' is available in the specified path.
    - Update the email and password fields with valid credentials.
    - Update the API endpoint URL according to actual requirements.
    Exceptions:
    - TimeoutException: If the email or password field, or the submit button is not found within the specified wait time.
    - requests.exceptions.RequestException: If there is an issue with the HTTP request to update the token.
    """
    try:

        # Get email, password, and URL from arguments
        email = sys.argv[1]
        password = sys.argv[2]
        mysite = sys.argv[3]

        chrome_options = webdriver.ChromeOptions()
        # Add your options as needed
        options = [
            # Define window size here
            "--window-size=1200,1200",
            "--ignore-certificate-errors",
            "--log-level=3",
            # "--headless",
            # "--disable-gpu",
            # "--window-size=1920,1200",
            # "--ignore-certificate-errors",
            # "--disable-extensions",
            # "--no-sandbox",
            # "--disable-dev-shm-usage",
            #'--remote-debugging-port=9222'
        ]

        for option in options:
            chrome_options.add_argument(option)

        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://results-service.ielts.org/")

        # Enter email
        email_field = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        email_field.send_keys(email)
        logging.info("Email entered.")

        # Enter password
        pwd_field = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        pwd_field.send_keys(password)
        logging.info("Password entered.")

        # Click login
        btn = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "auth0-lock-submit"))
        )
        btn.click()
        logging.info("Submit button clicked.")

        logging.info("Waiting for token in URL...")
        timeout = time.time() + 5  # 5分钟超时
        while time.time() < timeout:
            auth_headers = [
                req.headers.get("Authorization")
                for req in driver.requests
                if req.response
                and "results-service-api.ielts.org/api/dashboard" in req.url
            ]
            if len(auth_headers) > 0:
                id_token = auth_headers[0][len("Bearer ") :]
                break
            time.sleep(0.1)
        else:
            if "Wrong email or password." in driver.page_source:
                send_email(subject=email, body="Wrong email or password.")
                raise ValueError("Wrong email or password.")
            raise TimeoutError("Token retrieval timed out.")
        logging.info(f"token {id_token}")

        url = f"{mysite}{id_token}"
        response = requests.get(url)

        if response.status_code == 200:
            logging.info("Token updated successfully.")
        else:
            logging.error(
                f"Failed to update token. Status code: {response.status_code}"
            )

    except Exception as e:
        logging.error(f"Error in update_token: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    update_token()
