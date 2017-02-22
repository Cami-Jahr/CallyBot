import requests
import help_methods

class Reply:
    
    def __init__(self,access_token):
        self.access_token=access_token


    def arbitrate(self,user_id,data): #Chooses action based on message given
        # Might change to regex expressions later
        data_type,content=Reply.process_data(data)
        print ("Data type:",data_type)
        print ("Content:",content)
        if data_type=="unknown": #Cant handle unknown
            return
        # ------------ COMMANDOES --------------
        content_list=content.lower().split()
        if content_list[0] == "get":
            self.get_statements(user_id, content_list[1:])
        elif content_list[0] == "set":
            self.set_statements(user_id, content_list[1:])
        elif content=="hello":
            msg="http://cdn.ebaumsworld.com/mediaFiles/picture/2192630/83801651.gif"
            self.reply(user_id,msg,'image')
        elif content=="login":
            self.login(user_id)
        # ------------ HELP METHODS -----------
        elif content=="help":
            msg="Oh you need help?\nNo problem!\nFollowing commandoes are supported\n\n- hello\n- login\n- get deadlines\n\nBut thats not all, theres also some more!\nIts up to you to find them :)"
            self.reply(user_id,msg,'text')
        elif content=="hint":
            msg="This will be removed at launch!\n\n- juicy gif\n- who am I?\n- id"
            self.reply(user_id,msg,'text')
        # ------------ EASTER EGGS --------------
        #elif content=="chicken":
            #msg="http://folk.ntnu.no/halvorkm/TDT4140/chickenattack.mp4"
            #self.reply(user_id,msg,'video')
            pass
        elif content=="id":
            self.reply(user_id,user_id,'text')
        elif content=="juicy gif":
            msg="http://68.media.tumblr.com/tumblr_m9pbdkoIDA1ra12qlo1_400.gif"
            self.reply(user_id,msg,'image')
        elif content=="who am I?":
            fname,lname,pic=help_methods.get_user_info(self.access_token,user_id) # Get userinfo
            msg="You are "+fname+" "+lname+" and you look like this:"
            self.reply(user_id,msg,'text')
            self.reply(user_id,pic,'image')
        # ------------ GET STARTED --------------
        elif content=="get_started":
            fname,lname,pic=help_methods.get_user_info(self.access_token,user_id) # Get userinfo
            msg="Hi there "+fname+"!\nMy name is CallyBot, but you may call me Cally :)\nType 'help' to see the what you can do. Enjoy!" 
            self.reply(user_id,msg,'text')
        else:
            self.reply(user_id,content,data_type)

    def get_statements(self, user_id, content_list):
        if content_list[0] == "deadline" or content_list[0] == "deadlines":
            msg = "ItsLearning:\n" + help_methods.IL_scrape(user_id) +"BlackBoard:\n" + help_methods.BB_scrape(user_id)
            self.reply(user_id, msg,'text')
        else:
            self.reply(user_id, "I'm sorry, I'm not sure how to retrieve that", "text")

    def set_statements(self, user_id, content_list):
        self.reply(user_id, "I'm sorry, I'm not sure what you want me to remember", "text")


    def process_data(data): #Classifies data type and extracts the data
        try:
            content=data['entry'][0]['messaging'][0]['message'] #Pinpoint content
            if 'text' in content: #Check if text 
                content=content['text'] #Extract text
                data_type='text'
            elif 'attachments' in content: #Check if attachment
                content=content['attachments'][0]
                data_type=content['type'] #Extract attachment type
                if(data_type in ('image','audio','video','file')): #Extract payload based on type
                    content=content['payload']['url'] #Get attachement url
                else: #Must be either location or multimedia which only have payload
                    content=content['payload']
        except:
            try: #Check if get started
                content=data['entry'][0]['messaging'][0]['postback']['payload']
                data_type='text'
            except:
                data_type="unknown"
                content=""
        
        return data_type,content


    def reply(self,user_id,msg,msg_type):
        if msg_type=='text': #Text reply
            data={
                "recipient":{"id":user_id},
                "message":{"text":msg}
            }
        elif msg_type in ('image','audio','video','file'): #Media attachment reply
            data={
                "recipient":{"id":user_id},
                "message":{
                    "attachment":{
                        "type":msg_type,
                        "payload":{
                            "url":msg
                            }
                        }
                    }
                }
        else:
            print("Error: Type not supported")
            return
        response=requests.post(self.get_reply_url(),json=data)
        print(response.content)


    def login(self,user_id): #Login url to login
        fname,lname,pic=help_methods.get_user_info(self.access_token,user_id)
        url="https://folk.ntnu.no/halvorkm/TDT4140?userid="+str(user_id)+"?name="+fname+"%"+lname
        data = {
            "recipient": {"id": user_id},
            "message":{
                "attachment":{
                    "type":"template",
                    "payload":{
                        "template_type":"button",
                        "text":"Please login here:",
                        "buttons":[{
                            "type":"web_url",
                            "url":url,
                            "title":"Login via Feide",
                            "webview_height_ratio": "compact",
                            "messenger_extensions": True,
                            "fallback_url":url}]
                        }
                    }
                }
        }
        response=requests.post(self.get_reply_url(),json=data)
        print(response.content)


    def get_reply_url(self):
        return "https://graph.facebook.com/v2.8/me/messages?access_token="+self.access_token

