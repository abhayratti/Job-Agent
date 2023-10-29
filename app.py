import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

options = webdriver.ChromeOptions()

options.add_experimental_option("detach", True)
extension_path = '1.5.20_0.crx'
options.add_extension(extension_path)

driver_path = 'chromedriver-win64\chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

websites = ["https://boards.greenhouse.io/grammarly/jobs/5351466#app",
            "https://boards.greenhouse.io/vardaspace/jobs/4641142003#app", 
            "https://boards.greenhouse.io/grammarly/jobs/5351466#app"
            ]

####################################################
def open_simplify_login():
    driver.get('https://simplify.jobs/auth/login')
    
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, """//*[@id="__next"]/div/div/main/div/div[2]/div[1]/form/div[5]/span/button"""))
        )
        print("Page loaded successfully!")
    except:
        print("Error: Page did not load within the specified timeout!")
        driver.quit()

    proceed = input("Proceed [y/n]: ")

    if proceed == "y":
        after_login()
    else:
        driver.quit()

def after_login():
    main_window_handle = driver.current_window_handle

    for website in websites:
        driver.execute_script("window.open('');")
        
        driver.switch_to.window(driver.window_handles[-1])
        
        driver.get(website)
        time.sleep(2)

    driver.switch_to.window(main_window_handle)
    driver.close()

    for idx in range(len(websites)):
        driver.switch_to.window(driver.window_handles[idx])
        
        driver.refresh()
        time.sleep(2)

        current_url = driver.current_url
        
        try:
            parent_shadow_root = driver.find_element(By.ID, 'simplifyJobsContainer')
            nested_span = parent_shadow_root.find_element(By.TAG_NAME, "span")
            shadow_root1 = nested_span.shadow_root
            time.sleep(2)
            shadow_content = shadow_root1.find_element(By.ID, 'fill-button')
            time.sleep(2)
            shadow_content.click()
            time.sleep(10)
            print('application filled out')
        except:
            print("Fill not findable")
            driver.quit()
        
        submit_button = driver.find_element(By.ID, "submit_app")
        submit_button.click()

        time.sleep(4)

        if driver.current_url == current_url:
            print("Did not submit form")

            # missing_fields = driver.find_elements(By.XPATH, "//*[contains(@class, 'field-error')]")

            # while len(missing_fields) > 0:
            #     missing_field = missing_fields[0]
                
            #     try:
            #         preceding_element = missing_field.find_element(By.XPATH, "./preceding-sibling::*[1]")
            #         print(preceding_element)
                    
            #     except Exception as e:
            #         print(f"Could not find preceding element due to: {e}")
                
            #     missing_fields = driver.find_elements(By.XPATH, "//*[contains(@class, 'field-error')]")

            while True:
                pass

        else:
            print("Successfully submitted form.")
        
        time.sleep(2)
    
open_simplify_login()