
# CallyBot
NTNU Software Development Project - Team 57 Pentum </br></br>
CallyBot is a software project under development. Cally helps you with reminders, assignment deadlines and exam dates. More functions may be added in the future. Assignment deadlines are currently only supported for students using itslearning and Blackboard through Feide at NTNU. The only courses currently availible are NTNU courses, which means that the only exam dates you can get are from these courses. </br></br>
## Join and talk to CallyBot today
To talk with Cally click [here](http://m.me/CallyBot). The bot CallyBot will not answer until it is released public, or you are added as a test user. To be added as a test user, send her a message [here](http://m.me/CallyBot) and you will be added as soon as possible.

### Features
Upcoming information

## Instructions - How to set up CallyBot from scratch 
### 1. Create a Facebook page
First you have to [create](https://www.facebook.com/pages/create/) a Facebook page from which the bot will communicate through.<br /> 
Then choose what kind of page you want, it does not really matter. The only important thing is to make it through your own Facebook profile.
### 2. Create an app at Facebook developer
Go to [Facebook developer](https://developers.facebook.com/) and login. Go to **My apps** and select **Add a new app**.<br />
Write in a name for your app and choose category as **Apps for Messenger**.<br />
Next, go to the section **App Review for Messenger**, add **pages_messaging** and **pages_messaging_subscriptions** to submission.<br />
Before we check out the code find the section **Token Generator**, select your page and save the **Page Access Token** you get. We will use that later when we connect the bot and app together.
### 3. Setup the server
Now it is time to look at the code. First you have to pull all the files from the **master** branch. Be sure to install all the required libraries if you do not already have installed them. Currently we are using these libraries:
* mysqliclient - MySQLdb for python3, for connecting to mysql database.
* Flask - To handle post/get requests from Facebook.
* requests - To handle incoming data from Flask, and to send data.
* selenium - To webscrape and general interaction with websites<sup>1</sup>.
* pycrypto - To decrypt passwords from database<sup>2</sup>.
* apscheduler - To handle interrupts to check database for reminders.

To install all packages, locate requrements.txt and open your terminal and run
```
pip install -r requirements.txt
```

Go into the **server_main.py** file and locate the variable **ACCESS_TOKEN**. Switch the value with the token you generated earlier.<br />
Now when you run the **server_main.py** file the server will run locally. We want to put it online. To do so we use [ngrok](https://ngrok.com/download)<br />
To use it simply, run the exe file with arguments **http** and **used_port**. We have not specified any port in the code, so Flask will use the default which is 5000. For instance:
```
./ngrok http 5000
```
or
```
ngrok http 5000
```
Be sure to be in the folder in which ngrok was downloaded <br /><br />
If everything went as it should ngrok has now given you a https url which points to your local port.<br />
Copy this url then run the **server_main.py** file. The current code uses an MySQL server from NTNU, which requires the code to be launched from within NTNU's eduroam, or on a computer running the [NTNU VPN](https://innsida.ntnu.no/wiki/-/wiki/English/Install+VPN?_36_pageResourcePrimKey=915712). <br />
Now go back to the app creation page and click on **+ Add Product**. Choose **webhook** and click **New subscription** and select **Page**<br /><br />
Be sure to be in the folder in which ngrok was saved. <br /><br />
If everything went as it should, ngrok has now given you a https url which points to your local port.<br />
Copy this url and then run the **server_main.py** file.<br />
Now go back to the app creation page and click on **+ Add Product**. Choose **webhook**, click **New subscription** and select **Page**.<br /><br />
In the **Callback URL** field, paste the url you got from ngrok. In the **Verify Token** field type in "**verifytoken**". This is already chosen in the code, under the variable name **VERIFY_TOKEN** in **server_main.py**. You are free to change this if you like, just be sure that it matches.<br /><br />
In the **Subscription Fields**, choose **messages** and **messaging_postbacks**. <br />
Now cross your fingers and then press **Verify and save**. Now you should see a **POST** request in ngrok and server_main with **200 ok** or similar as answer. If you do not, go over the steps and see if you missed anything. <br /><br />
To complete the setup, go back to **Messenger** under **Products** and go to the **Webhooks** section. Select your page and make it subscribe to the webook. <br /><br />
Now you should be good to go! Have fun chatting! <br/><br />
<sup>1</sup>*To use selenium you need to add [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) to* __**PATH**__ *or put it in your standard exe folder*.<br />
<sup>2</sup> Pycrypto is not currently supported by python 3.6, but is supported by python versions up to 3.5.3. Requires [C++ 15 compilator](http://landinghub.visualstudio.com/visual-cpp-build-tools) to install. *Tested with 'Download Visual C++ Build Tools 2015'.*
#### Notes
Everytime you start ngrok you get a new url. Be sure to change the webhook url to this. Also, if you shut down ngrok (the url) for too long, the webhook will be disabled. To fix this, you need to first update it with the new url, then make the page resubscribe to the webhook. <br /><br />

## Coding Convention
In this project, the chosen coding convention is PEP 8 for the Python Code. Further detailed information can be found [here](https://www.python.org/dev/peps/pep-0008/#introduction).

## Support
Our team is here to help if you have any questions. There are several ways to get in touch with our team member:
* Get support by joining our communication channel on Facebook Messenger [here](http://m.me/CallyBot).
* Report issuses [here](https://github.com/Folstad/TDT4140/issues) by opening a Github Issue on our repository.
