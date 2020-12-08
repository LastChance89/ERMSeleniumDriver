'''
Created on Dec 7, 2020

@author: ksmit
'''

import sys
import configparser


def setupConfigFile(path, url, port):
    print("Beginning configuration of ini file")
    config = configparser.ConfigParser()
    config.read(path)
    config['selenium_web_configuration']['url'] = url
    config['selenium_web_configuration']['port'] = port
    with open(path, 'w') as configFile:
        config.write(configFile)
if __name__ == '__main__':
    setupConfigFile(sys.argv[1],sys.argv[2], sys.argv[3])
    