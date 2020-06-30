
from selenium import webdriver 
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import random
import string
import logging
import time



class WebDriver(object):

    def __init__(self, driverSelction):
        super().__init__()
            
        #Setup Logging 
        logging.basicConfig(filename = "testRun", level="INFO", filemode = 'w', format='%(asctime)s - %(levelname)s - %(message)s' )
        
        if(driverSelction == 'firefox'):
            self.driver = webdriver.Firefox();
        else:
            self.driver= webdriver.Chrome();  
        
        self.testUserName = random.choices(string.ascii_uppercase, k = 15)
        self.testUserPassword = random.choices(string.ascii_uppercase, k = 15)
        self.testUserHint = random.choices(string.ascii_uppercase, k = 15)
        # self.driver.implicitly_wait(10)

        
    def beginTests(self):
        self.errors = []
        logging.info("Beginning test suite")
        self.mainSitePage()
        self.testCreateAccount()
        self.testLoginHint()
        self.testLogin()
        self.noAdminOptions()
        self.testClientNavigation()
        self.testAccountRecordDisplay()
        self.testLogOut()
        
        if(len(self.errors) != 0):
            logging.info("The following tests have failed")
            for failedTests in self.errors: 
                logging.info(failedTests)
        else: 
            logging.info("All tests completed successfully")
        
        logging.info("Test suite completed")
        self.endTestandCleanUp()
    
    def mainSitePage(self):
        logging.info("Beginning Test: Navigating to main page")
        try:
            self.driver.get('http://localhost:8080/');
            assert "ERM" in self.driver.title
            time.sleep(1)
        except (NoSuchElementException, AssertionError,TimeoutException):
            self.errors.append("testCreateAccount")
            logging.exception("Error connecting to site")   
            self.endTestandCleanUp()
    
    def testCreateAccount(self):
        logging.info("Beginning Test: Creating Account")
        
        try:
            self.driver.find_element_by_id('createAccountLink').click()
            
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"create-label-display")))
            
            time.sleep(1)
            currentURL =  self.driver.current_url 
            assert  currentURL == "http://localhost:8080/#/login/createAccount"

            self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
            self.driver.find_element_by_id("hintInput").send_keys(self.testUserHint)
            self.driver.find_element_by_id("accButton").click()
            
            WebDriverWait(self.driver, 2).until(
                expected_conditions.presence_of_element_located((By.ID,"SuccessMessage")))
            
            self.driver.find_element_by_id("SuccessMessage")
            logging.info("Element found")
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("testCreateAccount")
            logging.exception("Error testing testCreateAccount")   
       
        self.driver.find_element_by_id("okButton").click();
        logging.info("Testing for creating account complete")

    def testLoginHint(self):
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
            self.errors.append("testLoginHint")
            logging.exception("Error testing login hint")
        
        #need to verify below. 
        # Password Hint: self.testUserHint 

    def testLogin(self):
        try:
            
            self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
            self.driver.find_element_by_id("loginUser").click()
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"login-user-container")))
            assert self.driver.current_url  == "http://localhost:8080/#/application"
            userToText = ''.join(self.testUserName)
            assert self.driver.find_element_by_id("loggedInUser").text ==  userToText
            
            assert self.driver.find_element_by_css_selector(".menu").is_displayed()
            logging.info("Login component testing successful")
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("testLogin")
            logging.exception("Error testing using login")
            
    def noAdminOptions(self):
        try:
            adminIsHidden = len(self.driver.find_elements(By.ID, "fileLoadLink")) == 0
            assert adminIsHidden == True
            logging.info("Admin Links not found for normal user")
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("noAdminOptions")
            logging.exception("Error testing noAdminOptions")
            self.endTestandCleanUp()

    def testClientNavigation(self):
        try:
            WebDriverWait(self.driver,10).until(expected_conditions.element_to_be_clickable((By.ID,"clientLink")))
            self.driver.find_element_by_id("clientLink").click()
            time.sleep(1)
            currentURL =  self.driver.current_url 
            logging.info(currentURL)
            assert currentURL == "http://localhost:8080/#/client"
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"grid-container")))
            linkExists = len(self.driver.find_elements(By.LINK_TEXT, "1114")) == 1
            assert linkExists == True
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.LINK_TEXT,"1114")))
            self.driver.find_element_by_link_text("1114").click()
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("testClientNavigation")
            logging.exception("Error testing testClientNavigation")
      
    def testAccountRecordDisplay(self):
        try:
            #First we check the client information that is displayed. We wait until its populated before checking.
            WebDriverWait(self.driver,10).until(expected_conditions.text_to_be_present_in_element
                                                ((By.XPATH,"//div[@class='record-display-container']/div/table/tr[1]/th[2]"),"1114"))
            time.sleep(1)
            currentURL =  self.driver.current_url 
            logging.info(currentURL)
            assert currentURL == "http://localhost:8080/#/records/1114"
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
            self.errors.append("testAccountRecordDisplay")
            logging.exception("Error testing testAccountRecordDisplay")
    
    def testLogOut(self):
        try:  
            self.driver.find_element_by_xpath("//div[@class='login-user-container']/div[2]/a").click()
            WebDriverWait(self.driver,10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"user-label-display")))
            currentURL =  self.driver.current_url 
            assert  currentURL == "http://localhost:8080/#/login" 
        except (NoSuchElementException, AssertionError, TimeoutException):
            self.errors.append("testLogOut")
            logging.exception("Error testing testLogOut")
    
    
    def endTestandCleanUp(self):
        self.driver.close()
        self.driver.quit()