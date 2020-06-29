
from selenium import webdriver 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import random
import string
import logging



class WebDriver(object):

    def __init__(self, driverSelction):
        super().__init__()
            
        #Setup Logging 
        logging.basicConfig(filename = "testRun", level="INFO", filemode = 'w', format='%(asctime)s - %(levelname)s - %(message)s' )
        
        if(driverSelction == 'firefox'):
            self.driver = webdriver.Firefox();
        else:
            self.driver= webdriver.Chrome();  
        
    def beginTests(self):
        self.errors = []
        logging.info("Beginning test suite")
        self.mainSitePage()
        self.testCreateAccount()
        self.testLoginHint()
        self.testLogin()
        self.noAdminOptions()
        self.testClientNavigation()
        self.testAccountHeader()
        
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
        except (NoSuchElementException, AssertionError):
            self.errors.append("testCreateAccount")
            logging.exception("ERROR:")   
            self.endTestandCleanUp()
    
    def testCreateAccount(self):
        logging.info("Beginning Test: Creating Account")
        
        self.testUserName = random.choices(string.ascii_uppercase, k = 15)
        self.testUserPassword = random.choices(string.ascii_uppercase, k = 15)
        self.testUserHint = random.choices(string.ascii_uppercase, k = 15)
        try:
            self.driver.find_element_by_id('createAccountLink').click()
            self.driver.implicitly_wait(1)
            assert self.driver.current_url == "http://localhost:8080/#/login/createAccount"
            logging.info(self.driver.current_url)
            self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
            self.driver.find_element_by_id("hintInput").send_keys(self.testUserHint)
            self.driver.find_element_by_id("accButton").click()
            
            WebDriverWait(self.driver, 2).until(
                expected_conditions.presence_of_element_located((By.ID,"SuccessMessage")))
            
            self.driver.find_element_by_id("SuccessMessage")
            logging.info("Element found")
        except (NoSuchElementException, AssertionError):
            self.errors.append("testCreateAccount")
            logging.exception("ERROR:")   
            self.endTestandCleanUp()
       
        self.driver.find_element_by_id("okButton").click();
        logging.info("Testing for creating account complete")




    def testLoginHint(self):
        try:
            self.driver.implicitly_wait(2)
            self.driver.find_element_by_id("forgetPasswordButton").click()
            WebDriverWait(self.driver,2).until(expected_conditions.presence_of_all_elements_located((By.CSS_SELECTOR,".modal-content")))
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
            logging.info("elementFound")
            pop.find_element_by_id("closeMOdalButtonAfterSucsess").click()
        except (NoSuchElementException, AssertionError):
            self.errors.append("testLoginHint")
            logging.exception("Error testing login hint")
        
        #need to verify below. 
        # Password Hint: self.testUserHint 

    def testLogin(self):
        try:
            self.driver.implicitly_wait(2)
            self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
            self.driver.find_element_by_id("loginUser").click()
            self.driver.implicitly_wait(3)
            assert self.driver.current_url == "http://localhost:8080/#/application"
            assert self.driver.find_element_by_css_selector(".menu").is_displayed()
            logging.info("Login component testing successful")
        except (NoSuchElementException, AssertionError):
            self.errors.append("testLogin")
            logging.exception("Error testing using login")
            
    def noAdminOptions(self):
        try:
            adminIsHidden = len(self.driver.find_elements(By.ID, "fileLoadLink")) == 0
            assert adminIsHidden == True
            logging.info("Admin Links not found for normal user")
        except (NoSuchElementException, AssertionError):
            self.errors.append("noAdminOptions")
            logging.exception("Error testing noAdminOptions")
            self.endTestandCleanUp()

    def testClientNavigation(self):
        try:
            WebDriverWait(self.driver,1).until(expected_conditions.presence_of_element_located((By.ID,"clientLink")))
            self.driver.find_element_by_id("clientLink").click()
            self.driver.implicitly_wait(1)
            assert self.driver.current_url == "http://localhost:8080/#/client"
            WebDriverWait(self.driver,1).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"grid-container")))
            linkExists = len(self.driver.find_elements(By.LINK_TEXT, "1114")) == 1
            assert linkExists == True
            self.driver.find_element_by_link_text("1114").click()
            self.driver.implicitly_wait(1)
        except (NoSuchElementException, AssertionError):
            self.errors.append("testClientNavigation")
            logging.exception("Error testing testClientNavigation")
      
    def testAccountHeader(self):
        try:
            WebDriverWait(self.driver,2).until(expected_conditions.presence_of_element_located((By.CLASS_NAME,"record-display-container")))
            assert self.driver.current_url == "http://localhost:8080/#/records/1114"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[1]/th[2]").text == "1114"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[1]/th[4]").text == "222 way Drive, Somewhere1 MD"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[2]/th[4]").text == "Service 1"
            assert self.driver.find_element_by_xpath("//div[@class='record-display-container']/div/table/tr[2]/th[2]").text == "Guy 214"
        except (NoSuchElementException, AssertionError):
            self.errors.append("testAccountHeader")
            logging.exception("Error testing testAccountHeader")
        
    def endTestandCleanUp(self):
        self.driver.close()
        self.driver.quit()