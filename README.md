# CallyBot
NTNU Software Development Project
## Instructions - How to set up CallyBot from scratch 
### 1. Create a Facebook page
First you have to [create](https://www.facebook.com/pages/create/) a Facebook page from which the bot will communicate through.<br /> 
Choose what kind of page you want, it doesnt really matter. The only important thing is to make it through your own Facebook profile.
### 2. Create an app at Facebook developer
Go to [Facebook developer](https://developers.facebook.com/) and login. Go to **My apps** and select **Add a new app**.<br />
Write in a name for your app and choose category as **Apps for Messenger**.<br />
Next go to the section **App Review for Messenger** and add **pages_messaging** and **pages_messaging_subscriptions** to submission.<br />
Before we check out the code find the section **Token Generator**, select your page and save the **Page Access Token** you get. We will use that later when we connect the bot and app together.
### 3. Setup the server
Now its time to look at the code. First you have to pull all the files from the branch **cally_server**. Be sure to install all the required libraries if you dont already have them. Currently we are using these:
* mysqliclient - MySQLdb for python3, for connecting to mysql database
* Flask - To handle post/get requests from Facebook
* requests - To handle incoming data from Flask, and to send data
* selenium - To webscrape and general interaction with website<sup>1</sup>

Go into the **server_main.py** file and locate the variable **ACCESS_TOKEN**. Switch the value with the token you generated earlier.<br />
Now when you run the **server_main.py** file the server will run locally. We want to put it online. To do so we use [ngrok](https://ngrok.com/download)<br />
To use it simply run the exe file with arguments **http** and **used_port**. We havent specified any port in the code, so Flask will use the default which is 5000. Example:<br />
```
./ngrok http 5000
```<br />
or <br />
```
ngrok http 5000
```

<sup>1</sup>To use selenium you need to add chromedriver to **PATH** or put it in your standard exe folder. 
