
from selenium import webdriver
from selenium.webdriver.common.keys import Keys; 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expectedCondition
import random
import string
import logging
from fileinput import filename



class WebDriver(object):
    '''
    classdocs
    '''
    

    
    def __init__(self, driverSelction):
        super().__init__()
        
        
        #Setup Logging 
        logging.basicConfig(filename = "testRun", level="INFO", filemode = 'w', format='%(asctime)s - %(levelname)s - %(message)s' )
        
        if(driverSelction == 'firefox'):
            self.driver = webdriver.Firefox();
        else:
            self.driver= webdriver.Chrome();  
        
    
    
    def beginTests(self):
        self.testCreateAccount()
        self.testLoginHint()
        #self.testLogin()
    
    def testCreateAccount(self):
        logging.info("Beginning test: Create account")
        
        self.driver.get('http://localhost:8080/');
        assert "ERM" in self.driver.title;
        self.driver.find_element_by_id('createAccountLink').click()
        self.testUserName = random.choices(string.ascii_uppercase, k = 15)
        self.testUserPassword = random.choices(string.ascii_uppercase, k = 15)
       
        
        self.testUserHint = random.choices(string.ascii_uppercase, k = 15)
        self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
        self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
        self.driver.find_element_by_id("hintInput").send_keys(self.testUserHint)
        self.driver.find_element_by_id("accButton").click()
        self.driver.implicitly_wait(2)
        try:
           #Does not work. Determine why as it might be a bit more elegant.   
           # WebDriverWait(self.driver, 2000).until(
           # expectedCondition.presence_of_element_located(self.driver.find_element_by_id("SuccessMessage")))
            
            self.driver.find_element_by_id("SuccessMessage")
            logging.info("Element found")
        except NoSuchElementException:
            logging.error("No element found")   
            self.endTestandCleanUp()
        
        self.driver.find_element_by_id("okButton").click();
        logging.info("Testing for creating account complete")




    def testLoginHint(self):
        try:
            self.driver.implicitly_wait(2)
            self.driver.find_element_by_id("forgetPasswordButton").click()
            self.driver.implicitly_wait(2)
            
            #Pop is web element, not web driver. 
            pop = self.driver.find_element_by_css_selector(".modal-dialog")
            pop.find_element_by_id("userNameInput").send_keys(self.testUserName)
            pop.find_element_by_id("gitHintButton").click()
            #self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
            self.driver.implicitly_wait(5)
            paragraph = pop.find_element_by_tag_name("p").text
          # self.driver.find_element_by_tag_name("p")
            hintToText = ''.join(self.testUserHint)
            paragraph == "Password Hint: " + hintToText
            logging.info("elementFound")
            pop.find_element_by_id("closeMOdalButtonAfterSucsess").click()
            
               
        except NoSuchElementException:
            logging.error("Error testing loginHint")
            self.endTestandCleanUp()
        
        #need to verify below. 
        # Password Hint: self.testUserHint 

    def testLogin(self):
        self.driver.implicitly_wait(2)
        self.driver.find_element_by_id("userNameInput").send_keys(self.testUserName)
        self.driver.find_element_by_id("passwordInput").send_keys(self.testUserPassword)
    def testNavigate(self):
        b = 1
    def testFindClient(self):
        c =1 
    def testGoToRecords(self):
        d=1
    
    def endTestandCleanUp(self):
        #self.driver.close()
        self.driver.quit()