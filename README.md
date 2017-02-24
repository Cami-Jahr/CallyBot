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
Now when you run the **server_main.py** file the server will run locally. We want to put it online. To do so we use **ngrok**

<sup>1</sup>To use selenium you need to add chromedriver to **PATH** or put it in your standard exe folder. 
