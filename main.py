from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from random import randint
import time

def main():
	file = open('config.txt','r') # Reading the config file
	data = file.readlines()
	file.close()

	mail = data[0].split(':')[-1].strip() # Extracting data from config file
	passw = data[1].split(':')[-1].strip()
	search = data[2].split(':')[-1].strip()
	location = data[3].split(':')[-1].strip()
	tm = int(data[4].split(':')[-1].strip())
	distance = data[5].split(':')[-1].strip()


	def login(driver):
		'''
		Login function used to login into linkedin with the bot
		'''
		driver.get('https://www.linkedin.com/checkpoint/lg/sign-in-another-account')
		condition = EC.visibility_of_element_located((By.CSS_SELECTOR, '#username'))
		first_option = WebDriverWait(driver, 15).until(condition)
		first_option.send_keys(mail)

		condition = EC.visibility_of_element_located((By.CSS_SELECTOR, '#password'))
		first_option = WebDriverWait(driver, 15).until(condition)
		first_option.send_keys(passw)

		condition = EC.visibility_of_element_located((By.CSS_SELECTOR, '.btn__primary--large'))
		first_option = WebDriverWait(driver, 15).until(condition)
		first_option.click()

	options = webdriver.ChromeOptions() # Estabilishing the settings for the driver
	options.add_experimental_option('excludeSwitches', ['enable-logging']) # Removing the chrome logs
	caps = DesiredCapabilities().CHROME 
	caps["pageLoadStrategy"] = "eager" # Making the bot not wait for page to completely load
	driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),options=options,desired_capabilities=caps)
	driver.maximize_window() # Converting window to full screen
	login(driver) # Logging in
	actions = ActionChains(driver) # Used to automate some actions via the keyboard, basically during scraping it needs to scroll down 

	while 'feed' not in driver.current_url: # After login feed keyword comes up in the URL
		pass

	print('Login success!')
	driver.get('https://www.linkedin.com/jobs/') # goes to jobs page

	for i in range(0,100000,25):
		lst = []
		driver.get(f'https://www.linkedin.com/jobs/search/?f_AL=true&distance={distance}&keywords={search}&location={location}&start={i}') # Visiting the page with specific job,location and page number
		l = []
		l_2 = []

		print('>>> Scraping Job listings')
		while len(l)<25: # Each page has exact 25 listings 
			soup = BeautifulSoup(driver.page_source,'html.parser') 
			k = soup.find_all('a',{'class':'disabled ember-view job-card-container__link'}) # Scraping all jobs
			for y in k:
				try:
					if 'jobs/view' in y.get('href'): # Extracting job url
						if y.get('href') not in l: # Checking if url is already processed
							l.append(y.get('href'))
							actions.send_keys(Keys.TAB) # Sending TAB press to scroll down to scrape more data
							actions.perform()
							lst.append('https://www.linkedin.com/'+y.get('href')) # Appending the complete URL into the list
				except Exception as e:
					pass

		print(f'>>> Total {len(lst)} jobs found on page {i}')

		for ln in lst: # Passing through the list
			driver.get(ln)
			n=0
			try:
				elm = driver.find_element_by_xpath('/html/body/div[6]/div[3]/div/div[1]/div[1]/div/div[1]/div[1]/div[3]/div/ul/li/span[1]')
				if 'submitted' in elm.text: # Checking if it already submitted the application
					n=1
					break 
			except:
				pass

			if n==0: # If not submitted already
				btn = ''
				while btn=='':
					try:
						soup = BeautifulSoup(driver.page_source,'html.parser') # Getting the apply buttons id 
						btn = soup.find('button',{'class':'jobs-apply-button artdeco-button artdeco-button--3 artdeco-button--primary ember-view'}).get('id')
						break
					except:
						try:
							lb = soup.find('a',{'aria-label':'Download your submitted resume'})
							lb.get('href')
							n=1
							print('>>> Have already applied for this job')
							break
						except:
							pass

			if n==0: # If apply button was found
				while True:
					elm = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{btn}')))
					driver.execute_script("arguments[0].click();", elm) # Clicking it

					btn = ''
					while btn=='':
						try:
							soup = BeautifulSoup(driver.page_source,'html.parser')
							btn = soup.find('div',{'class':'display-flex justify-flex-end ph5 pv4'}).find('button').get('id') # Finding the button on the apply pop up
							break
						except:
							pass

					elm = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#{btn}')))
					break

				if elm.get_attribute('aria-label')=='Submit application': # If the button on pop up says submit application then it will click
					driver.execute_script("arguments[0].click();", elm)
					print('>>> Job application submitted succesfully')
				
			n = randint(1,60) # Adding a randomized millisecond to make delay different in each listing
			print(f'>>> Visiting next job in {tm}.{n} seconds')
			time.sleep(tm+n//100)

main()