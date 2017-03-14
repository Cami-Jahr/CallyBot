from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from collections import deque


class Facebook_tester:

	def login(self):
		options = webdriver.ChromeOptions()
		prefs = {"profile.default_content_setting_values.notifications": 2}  #Settings to remove pupups
		options.add_experimental_option("prefs", prefs)
		self.driver = webdriver.Chrome(chrome_options=options)  #Open Chrome with settings
		self.driver.get("http://www.facebook.com")
		elem = self.driver.find_element_by_id("email")
		elem.send_keys("jokki.reserve@gmail.com")
		elem = self.driver.find_element_by_id("pass")
		elem.send_keys("123abc123")
		elem.submit()
		#Login complete
		#self.driver.get('https://www.facebook.com/messages/t/joachim.jahr.5') # Used for testing outside cally
		self.driver.get('https://www.facebook.com/messages/t/167935107030338') #Direct link to chat with cally
		self.elem = self.driver.find_element_by_class_name("_5rpu") #Text feild
		time.sleep(3) # Let chat history load propperly, can be removed

	def ask_with_simple_text_responses(self):
		"""Should currently only contain queries where the answers are single text answers. Must add funcionality for multiple answers, or another method"""
		help_answer = "Oh you need help?\nNo problem!\nFollowing commandoes are supported\n\n- hello\n- login\n- get deadlines [in <course>][until <DD/MM>]\n\nBut thats not all, theres also some more!\nIts up to you to find them "
		hint_answer = "This will be removed at launch!\n\n- juicy gif\n- juice gif\n- who am I?\n- who are you?\n- chicken\n- id"
		deadline_itslearning = "ItsLearning:\nAssignment 2: Demonstrated learning of Core 1\nin TDT4140 PROGRAMVAREUTVIKL\nDue date: 10.03.2017 23:55\n\nKTN1\nin TTM4100 KOMM TJEN NETT\nDue date: 10.03.2017 23:59\n\nDesignøving 2\nin TDT4180 MMI\nDue date: 24.03.2017 23:59\n\nAssignment 7 - Theory\nin TTM4100 KOMM TJEN NETT\nDue date: 26.03.2017 23:59"
		deadline_blackboard = "BlackBoard:\nnnlevering av rapport til eksperimentelt prosjekt\nin TFY4125 Fysikk\nDue date: 08.03.17\n\nTest 2 - middels\nin TFY4125 Fysikk\nDue date: 05.05.17\n\nTest 1 - middels\nin TFY4125 Fysikk\nDue date: 05.05.17\n\nDatabaseprosjekt - innlevering 2\nin TDT4145 Datamodellering og databasesystemer\nDue date: 16.03.17"
		startup_answer = "Hi there Joachim!\nMy name is CallyBot, but you may call me Cally \nType 'help' to see the what you can do. Enjoy!"
		# Queries to ask, nr is number of replies
		queries = deque([(1,"First test query"), 	#1
						 (1,"get_started"),
						 (1,"help"),
						 (1,"HELP"),
						 (1,"hint"),  				#5
						 (3,"get deadline")])
		# Swapped to correspond to queries
		answers = deque(["first test query", 	#1
						 startup_answer,
						 help_answer,
						 help_answer,
						 hint_answer, 			#5
						 "I'll go get your deadlines right now", deadline_itslearning, deadline_blackboard])
		next_question = queries.popleft
		next_answer = answers.popleft
		while queries: #Ask and check while there are queries left
			#print(queries)
			number, question = next_question()
			self.elem.send_keys(question)
			self.elem.send_keys(Keys.ENTER)  # Simples way to send messages
			sent = True	#Wait for answer
			old_elems = self.driver.find_elements_by_css_selector("._3oh-._58nk")  # This is the class name for single messages, but accessed with css selector due to having spaces in the name
			seen = old_elems.__len__()  # Number of old messages
			while sent:
				new_elems = self.driver.find_elements_by_css_selector("._3oh-._58nk")
				now_amount = new_elems.__len__() #Number of current messeges in chat
				print(seen, now_amount, number)
				#print("new",now_amount, "old", seen)
				if seen + number == now_amount:  # If there are any new messages
					for i in range(seen, now_amount):
						expected = next_answer()
						print("Got:"+new_elems[i].text+"\nExpected:"+expected) #print all new messages, not including testers, in order they were writen
						if new_elems[i].text != expected:
							print("-----------------------ERROR----------------------")
						else:
							print("######################Correct#####################")
						print("\n")
						###########################################
						###					####				###
						### SHOULD BE CHANGED TO JUNIT TESTING  ###
						###					####				###
						###########################################

					sent = False  # Tester should send next question
				else:
					time.sleep(10) #Waiting time in pooling. in sec
					print("...")


if __name__ == '__main__':
	tester = Facebook_tester()
	tester.login()
	print("Setup complete!\n")
	tester.ask_with_simple_text_responses()
	print("Testing completed!")
