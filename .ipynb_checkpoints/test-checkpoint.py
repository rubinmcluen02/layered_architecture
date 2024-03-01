import unittest
import uuid
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class FlaskAppSeleniumTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()

    def tearDown(self):
        self.driver.close()
        self.driver.quit()

    def test_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/patient_login")

        username_field = driver.find_element(By.NAME, "username")
        password_field = driver.find_element(By.NAME, "password")

        username_field.send_keys("test")
        password_field.send_keys("Pass1")

        login_button = driver.find_element(By.XPATH, '//input[@value="Login"]')
        login_button.click()
        
        success_message = driver.find_element(By.ID, "success_message")
        self.assertIn("Welcome", success_message.text)
        
    def test_register_account(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/register")
        unique_username = f"user_{uuid.uuid4()}"

        driver.find_element(By.ID, "username").send_keys(unique_username)
        driver.find_element(By.ID, "password").send_keys("Pass1")
        driver.find_element(By.ID, "confirm_password").send_keys("Pass1")
        
        security_question = driver.find_element(By.ID, "security_question")
        security_question.find_element(By.CSS_SELECTOR, "option[value='1']").click()
        driver.find_element(By.ID, "security_answer").send_keys("Fluffy")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        WebDriverWait(driver, 10).until(EC.url_to_be("http://127.0.0.1:5000/patient_login"))

    def test_change_password(self):
            driver = self.driver
            driver.get("http://127.0.0.1:5000/change_password")

            driver.find_element(By.NAME, "username").send_keys("user1")
            driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "answer"))
            )

            driver.find_element(By.NAME, "answer").send_keys("Fluffy")
            driver.find_element(By.NAME, "new_password").send_keys("Pass1")
            driver.find_element(By.NAME, "confirm_new_password").send_keys("Pass1")

            driver.find_element(By.CSS_SELECTOR, "input[value='Change Password']").click()

            WebDriverWait(driver, 10).until(
                EC.url_to_be("http://127.0.0.1:5000/patient_login")
            )

if __name__ == '__main__':
    unittest.main()
