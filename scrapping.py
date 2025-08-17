from tenacity import retry, wait_fixed, stop_after_attempt
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
@retry(wait=wait_fixed(3), stop=stop_after_attempt(3), reraise=True)
def login_instagram_and_navigate_to_profile(profile: str):
    logger.info(f"Logging into Instagram...")
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get("https://www.instagram.com/")
    
    # click on allow cookies button
    allow_cookies_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Allow all cookies']")))
    allow_cookies_button.click()


    username_field = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password_field = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username_field.send_keys("randomgenstudio@writeme.com")
    password_field.send_keys("FTmFQ8hyHmrJRDl@7Y1K!Je5IuP8*")

    login_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
    login_button.click()

    time.sleep(10)
    logger.info(f"Navigating to {profile}")
    driver.get(f"https://www.instagram.com/{profile}/")

    return driver


def scroll_searching_new_posts(driver, already_detected_posts=[], total_allowed_duplicated_posts=None):
    soups = []

    initial_height = driver.execute_script("return document.body.scrollHeight")

    retry_timeout = 30  # Seconds to wait for new content
    post_ids = set()
    duplicated_detection_count = 0
    while True:
        # Capture current page content
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        soups.append(soup)
        
        elements = soup.find_all('a', class_="x1i10hfl xjbqb8w x1ejq31n x18oe1m7 x1sy0etr xstzfhl x972fbf x10w94by x1qhh985 x14e42zd x9f619 x1ypdohk xt0psk2 x3ct3a4 xdj266r x14z9mp xat24cr x1lziwak xexx8yu xyri2b x18d9i69 x1c1uobl x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")
        for element in elements:
            href = element.get('href')
            post_id = href.split("/")[-2]
            if post_id not in already_detected_posts and post_id not in post_ids:
                post_ids.add(post_id)
                logger.info(f"Detected new post ID: {post_id}")
            elif post_id not in post_ids:
                duplicated_detection_count += 1
        
        # Scroll to trigger new content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for new content with timeout
        start_time = time.time()
        new_height = initial_height
        
        while True:
            # Check for height change every second
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            if new_height > initial_height:
                break  # New content detected
            
            if time.time() - start_time >= retry_timeout :
                logger.info("Timeout reached")
                break  # Timeout reached
        # Exit condition - no new content after timeout
        if new_height == initial_height:
            break
        if total_allowed_duplicated_posts:
            logger.info(f"Duplicated detection count: {duplicated_detection_count}")
            if duplicated_detection_count >= total_allowed_duplicated_posts:
                logger.info("Maximum allowed duplicated posts reached.")
                break
        
        # Update height for next iteration
        initial_height = new_height
    
    return post_ids