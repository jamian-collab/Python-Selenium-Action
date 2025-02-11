from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import logging
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
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

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

    
driver = webdriver.Chrome(options = chrome_options)

def update_token():
    """
    该函数自动化登录IELTS成绩服务网站，获取URL中的认证token，并通过发送到指定API端点来更新token。
    函数执行的步骤：
    1. 使用特定选项初始化Chrome WebDriver，以无头模式运行并抑制日志。
    2. 打开IELTS成绩服务网站。
    3. 输入邮箱和密码进行登录。
    4. 点击提交按钮登录。
    5. 等待URL包含认证token。
    6. 从URL中提取token。
    7. 将token发送到指定的API端点进行更新。
    8. 打印token更新操作的状态。
    注意：
    - 确保'chromedriver.exe'在指定路径中可用。
    - 使用有效的凭据更新邮箱和密码字段。
    - 根据实际端点要求更新API端点URL。
    异常：
    - TimeoutException: 如果在指定等待时间内未找到邮箱或密码字段，或提交按钮。
    - requests.exceptions.RequestException: 如果HTTP请求更新token时出现问题。
    """
    try:
        op = Options()
        op.add_argument("--no-sandbox")
        op.add_argument("--headless")
        op.add_argument("--disable-gpu")
        op.add_argument("--log-level=3")  # 设置日志级别为3，抑制错误信息
        op.add_experimental_option("detach", True)

        se = Service("chromedriver.exe")
        driver = webdriver.Chrome(service=se, options=op)
        driver.maximize_window()
        driver.get("https://results-service.ielts.org/")

        # 输入邮箱
        email_field = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        email_field.send_keys("zkielts@163.com")
        logging.info("Email entered.")

        # 输入密码
        pwd_field = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
        pwd_field.send_keys("Abc13717421!")
        logging.info("Password entered.")

        # 点击登录
        btn = WebDriverWait(driver, 300).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "auth0-lock-submit"))
        )
        btn.click()
        logging.info("Submit button clicked.")

        logging.info("Waiting for token in URL...")
        timeout = time.time() + 300  # 5分钟超时
        while time.time() < timeout:
            pattern = (
                r"https://results-service\.ielts\.org/#id_token=([^&]+)&state=([^&]+)"
            )
            match = re.search(pattern, driver.current_url)
            if match:
                id_token = match.group(1)
                break
            time.sleep(0.1)
        else:
            raise TimeoutError("Token retrieval timed out.")

    except Exception as e:
        logging.error(f"Error in update_token: {e}")
    finally:
        driver.quit()

update_token()

