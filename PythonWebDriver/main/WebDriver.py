
from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import random
import string
import logging
import time
from datetime import date
import configparser

class WebDriver(object):

    def __init__(self, driverSelction):
        super().__init__()
        config = configparser.ConfigParser()

        config.read("configuration.ini")

        self.url ="http://"+ config['selenium_web_configuration']['url'] + ":" + config['selenium_web_configuration']['port']
       
        #print("HERE IS MY URL " + self.url)
        
        log_name ="output_" + date.today().strftime("%d_%m_%Y")
        #Setup Logging 
        logging.basicConfig(filename = log_name, level="INFO", filemode = 'w', format='%(asctime)s - %(levelname)s - %(message)s' )
        
        'This is so we dont have to bother about installing the proper version of chrome installer'
        options= webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-extensions")
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=options)

        
        '''
        @TODO: Implement this with real webdriver manager later. Chome only supported browser for now
        Will need to make adjustments cause I know there are some CSS issues with firefox.
        if(driverSelction == 'firefox'):
            self.driver = webdriver.Firefox();
        else:
            self.driver= webdriver.Chrome();  
        '''
        self.testUserName = random.choices(string.ascii_uppercase, k = 15)
        self.testUserPassword = random.choices(string.ascii_uppercase, k = 15)
        self.testUserHint = random.choices(string.ascii_uppercase, k = 15)
        # self.driver.implicitly_wait(10)

        
    def begin_tests(self):
        self.errors = []
        logging.info("Beginning test suite")
        self.main_site_page()
        self.test_create_account()
        self.test_login_hint()
        self.test_login()
        self.no_admin_options()
        self.test_client_navigation()
        self.test_account_record_display()
        self.test_log_out()
        
        if(len(self.errors) != 0):
            logging.info("The following tests have failed")
            for failedTests in self.errors: 
                logging.info(failedTests)
        else: 
            logging.info("All tests completed successfully")
        
        logging.info("Test suite completed")
        self.end_test_and_cleanup()
    
    def main_site_page(self):
        logging.info("Beginning Test: Navigating to main page")
        try:
            self.driver.get(self.url);
            assert "ERM" in self.driver.title
            time.sleep(1)
        except (NoSuchElementException, AssertionError,TimeoutException):
            self.errors.append("test_create_account")
            logging.exception("Error connecting to site")   
            self.end_test_and_cleanup()
    
    def test_create_account(self):
        logging.info("Beginning Test: Creating Account")
        
        try:
            self.driver.find_element_by_id('createAccountLink').click()
            
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"create-label-display")))
            time.sleep(1)
            currentURL =  self.driver.current_url 
            
            assert  currentURL == self.url + "/#/login/createAccount"
         
            time.sleep(1)
            self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
            self.driver.find_element_by_id("hintInput").send_keys(self.testUserHint)
            self.driver.find_element_by_id("accButton").click()
            
            WebDriverWait(self.driver, 2).until(
                expected_conditions.presence_of_element_located((By.ID,"SuccessMessage")))
            
            self.driver.find_element_by_id("SuccessMessage")
            logging.info("Element found")
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("test_create_account")
            logging.exception("Error testing test_create_account")   
        
        time.sleep(1)
        self.driver.find_element_by_id("okButton").click();
        logging.info("Testing for creating account complete")

    def test_login_hint(self):
        try:
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"user-label-display")))
            self.driver.find_element_by_id("forgetPasswordButton").click()
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR,".modal-content")))
            #Pop is web element, not web driver. 
            pop = self.driver.find_element_by_css_selector(".modal-dialog")
            pop.find_element_by_id("userNameInput").send_keys(self.testUserName)
            pop.find_element_by_id("gitHintButton").click()
            '''
            We add the WebDriverWait here because the modal refreshes, and the p element is removed from the DOM
            which throws a stale element exception
            '''
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR,".message-container")))
            paragraph = pop.find_element_by_tag_name("p").text
            hintToText = ''.join(self.testUserHint)
            assert paragraph == "Password Hint: " + hintToText
            pop.find_element_by_id("closeMOdalButtonAfterSucsess").click()
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("test_login_hint")
            logging.exception("Error testing login hint")
        
        #need to verify below. 
        # Password Hint: self.testUserHint 

    def test_login(self):
        try:
            
            self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
            self.driver.find_element_by_id("loginUser").click()
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"login-user-container")))
            assert self.driver.current_url  == self.url + "/#/application"
            userToText = ''.join(self.testUserName)
            assert self.driver.find_element_by_id("loggedInUser").text ==  userToText
            
            assert self.driver.find_element_by_css_selector(".menu").is_displayed()
            logging.info("Login component testing successful")
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("test_login")
            logging.exception("Error testing using login")
            
    def no_admin_options(self):
        try:
            adminIsHidden = len(self.driver.find_elements(By.ID, "fileLoadLink")) == 0
            assert adminIsHidden == True
            logging.info("Admin Links not found for normal user")
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("no_admin_options")
            logging.exception("Error testing no_admin_options")
            self.end_test_and_cleanup()

    def test_client_navigation(self):
        try:
            WebDriverWait(self.driver,10).until(expected_conditions.element_to_be_clickable((By.ID,"clientLink")))
            self.driver.find_element_by_id("clientLink").click()
            time.sleep(1)
            currentURL =  self.driver.current_url 
            logging.info(currentURL)
            assert currentURL == self.url +"/#/client"
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"grid-container")))
            linkExists = len(self.driver.find_elements(By.LINK_TEXT, "1114")) == 1
            assert linkExists == True
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.LINK_TEXT,"1114")))
            self.driver.find_element_by_link_text("1114").click()
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("test_client_navigation")
            logging.exception("Error testing test_client_navigation")
      
    def test_account_record_display(self):
        try:
            #First we check the client information that is displayed. We wait until its populated before checking.
            WebDriverWait(self.driver,10).until(expected_conditions.text_to_be_present_in_element
                                                ((By.XPATH,"//div[@class='record-display-container']/div/table/tr[1]/th[2]"),"1114"))
            time.sleep(1)
            currentURL =  self.driver.current_url 
            logging.info(currentURL)
            time.sleep(1)
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[1]/th[2]").text == "1114"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[1]/th[4]").text == "222 way Drive, Somewhere1 MD"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[2]/th[4]").text == "Service 1"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[2]/th[2]").text == "Guy 214"
            
            #Next, to just check we have data on the grid, we check the first row. 
            assert self.driver.find_element_by_xpath("//div[@class='ag-row ag-row-no-focus ag-row-even ag-row-level-0 ag-row-position-absolute ag-row-first']/div[1]").text =="06/07/17"     
            assert self.driver.find_element_by_xpath("//div[@class='ag-row ag-row-no-focus ag-row-even ag-row-level-0 ag-row-position-absolute ag-row-first']/div[2]").text =="$4.13" 
            assert self.driver.find_element_by_xpath("//div[@class='ag-row ag-row-no-focus ag-row-even ag-row-level-0 ag-row-position-absolute ag-row-first']/div[3]").text =="12.59 kWh" 
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("test_account_record_display")
            logging.exception("Error testing test_account_record_display")
    
    def test_log_out(self):
        try:  
            self.driver.find_element_by_xpath("//div[@class='login-user-container']/div[2]/a").click()
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"user-label-display")))
            currentURL =  self.driver.current_url 
            assert  currentURL == self.url +"/#/login" 
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("test_log_out")
            logging.exception("Error testing test_log_out")
    
    
    def end_test_and_cleanup(self):
        self.driver.close()
        self.driver.quit()