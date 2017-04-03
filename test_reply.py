import reply
import credentials
import unittest
import callybot_database
credential = credentials.Credentials()
db = callybot_database.CallybotDB(*credential.db_info)
replier = reply.Reply(credential.access_token, db)


class Tester(unittest.TestCase):
    def test_process_data(self):
        test_data_message = {
            'entry': [{'messaging': [{'message': 'this is message'}]}]}  # check for message not text or attachment
        data_type, content = reply.Reply.process_data(test_data_message)
        self.assertEqual(data_type, "unknown")
        self.assertEqual(content, "")

        test_data_text = {'entry': [{'messaging': [{'message': {'text': 'this is text'}}]}]}  # check for text string
        data_type, content = reply.Reply.process_data(test_data_text)
        self.assertEqual(data_type, "text")
        self.assertEqual(content, "this is text")

        test_data_type = {'entry': [
            {'messaging': [{'message': {'attachments': [{'type': 'this is a type'}]}}]}]}  # check for nonexistent type
        data_type, content = reply.Reply.process_data(test_data_type)
        self.assertEqual(data_type, "unknown")
        self.assertEqual(content, "")

        test_data_image = {'entry': [{'messaging': [{'message': {
            'attachments': [{'type': 'image', 'payload': {'url': 'this is image url'}}]}}]}]}  # check for image
        data_type, content = reply.Reply.process_data(test_data_image)
        self.assertEqual(data_type, "image")
        self.assertEqual(content, "this is image url")

        test_data_video = {'entry': [{'messaging': [{'message': {
            'attachments': [{'type': 'video', 'payload': {'url': 'this is video url'}}]}}]}]}  # check for video
        data_type, content = reply.Reply.process_data(test_data_video)
        self.assertEqual(data_type, "video")
        self.assertEqual(content, "this is video url")

        test_data_file = {'entry': [{'messaging': [{'message': {
            'attachments': [{'type': 'file', 'payload': {'url': 'this is file url'}}]}}]}]}  # check for file
        data_type, content = reply.Reply.process_data(test_data_file)
        self.assertEqual(data_type, "file")
        self.assertEqual(content, "this is file url")

        test_data_audio = {'entry': [{'messaging': [{'message': {
            'attachments': [{'type': 'audio', 'payload': {'url': 'this is audio url'}}]}}]}]}  # check for audio
        data_type, content = reply.Reply.process_data(test_data_audio)
        self.assertEqual(data_type, "audio")
        self.assertEqual(content, "this is audio url")

        test_data_multimedia = {'entry': [{'messaging': [{'message': {
            'attachments': [{'type': 'multimedia', 'payload': 'this is multimedia url'}]}}]}]}  # check for multimedia
        data_type, content = reply.Reply.process_data(test_data_multimedia)
        self.assertEqual(data_type, "multimedia")
        self.assertEqual(content, "this is multimedia url")

        test_data_geolocation = {'entry': [{'messaging': [{'message': {'attachments': [
            {'type': 'geolocation', 'payload': 'this is geolocation url'}]}}]}]}  # check for geolocation
        data_type, content = reply.Reply.process_data(test_data_geolocation)
        self.assertEqual(data_type, "geolocation")
        self.assertEqual(content, "this is geolocation url")

        test_data_quick_reply = {'entry': [{'messaging': [
            {'message': {'quick_reply': {'payload': "this is reply"},
                         'text': 'this is text'}}]}]}  # check for quick reply
        data_type, content = reply.Reply.process_data(test_data_quick_reply)
        self.assertEqual(data_type, "text")
        self.assertEqual(content, "this is reply")

    def test_arbitrate(self):
        test_id = "123456789"

        test_text = {'entry': [{'messaging': [{'message': {'text': 'hint'}}]}]}  # check for text string
        msg = "This will be removed at launch!\n\n- Juicy gif\n- Juice gif\n- Who am I?\n- Who are you?\n- " \
                     "Chicken\n- Hello\n- Good bye"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'yes, i agree to delete all my information'}}]}]}  # check for text string
        msg = "I have now deleted all your information. If you have any feedback to give me, please " \
                  "do so with the 'request' function.\nI hope to see you again!."
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'hello'}}]}]}  # check for text string
        msg = "http://cdn.ebaumsworld.com/mediaFiles/picture/2192630/83801651.gif"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'hi'}}]}]}  # check for text string
        msg = "http://cdn.ebaumsworld.com/mediaFiles/picture/2192630/83801651.gif"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'juice gif'}}]}]}  # check for text string
        msg = "https://i.makeagif.com/media/10-01-2015/JzrY-u.gif"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'juicy gif'}}]}]}  # check for text string
        msg = "http://68.media.tumblr.com/tumblr_m9pbdkoIDA1ra12qlo1_400.gif"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'who are you?'}}]}]}  # check for text string
        msg = "https://folk.ntnu.no/halvorkm/callysavior.jpg"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'who am i?'}}]}]}  # check for text string
        msg = ":)"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'good bye'}}]}]}  # check for text string
        msg = "http://i.imgur.com/NBUNSSG.gif"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'rick'}}]}]}  # check for text string
        msg = "https://media.giphy.com/media/Vuw9m5wXviFIQ/giphy.gif"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'image')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'start_new_chat'}}]}]}  # check for text string
        msg = "Welcome Does not!\nMy name is CallyBot, but you may call me Cally :)\nI will keep you up to " \
                                   "date on your upcoming deadlines on itslearning and Blackboard. Type 'login' " \
                                   "or use the menu to get started. \nIf you need help, or want to know more " \
                                   "about what I can do for you, just type 'help'.\n\nPlease do enjoy!"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'most_likely_command_was_not_true'}}]}]}  # check for text string
        msg = "Im sorry I was not able to help you. Please type 'help' to see my supported commands, or 'help " \
              "<feature>' to get information about a specific feature, or visit my " \
              "wiki https://github.com/Folstad/TDT4140/wiki/Commands.\nIf you believe you found a bug, or have a " \
              "request for a new feature or command, please use the 'bug' and 'request' commands"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'developer something'}}]}]}  # check for text string
        msg =  "Sorry, but these commands are only for developers. Type 'help' or visit " \
               "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get'}}]}]}  # check for text string
        msg = "Please specify what to get. Type 'help' or visit " \
               "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get deadlines'}}]}]}  # check for text string
        msg = "I'll go get your deadlines right now. If there are many people asking for deadlines this might take me some time."
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get profile'}}]}]}  # check for text string
        msg = "Hello Does not Exist!\nYou are not subscribed to any courses\nYou do not have any active reminders"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get reminders'}}]}]}  # check for text string
        msg = "You don't appear to have any reminders scheduled with me"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get exams'}}]}]}  # check for text string
        msg = "I could not find any exam date, are you sure you are subscribed to courses?"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get exam TDT4145'}}]}]}  # check for text string
        msg = "The exam in tdt4145 is on 2017-06-07\n\n"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get exam TDTPOTET'}}]}]}  # check for text string
        msg = "I cant find the exam date for tdtpotet\n\n"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get default'}}]}]}  # check for text string
        msg =  "Your default-time is: 1 day(s)"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get links'}}]}]}  # check for text string
        msg = "Blackboard:\nhttp://iblack.sexy\nItslearning:\nhttp://ilearn.sexy"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get link itslearning'}}]}]}  # check for text string
        msg = "Itslearning:\nhttp://ilearn.sexy"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get link blackboard'}}]}]}  # check for text string
        msg = "Blackboard:\nhttp://iblack.sexy"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'subscribe TDT4100'}}]}]}  # check for text string
        msg = None
        response = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get subscribed'}}]}]}  # check for text string
        msg = "You are subscribed to:\nTDT4100\n"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'get exams'}}]}]}  # check for text string
        msg = "The exam in TDT4100 is on 2017-05-16\n\n"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'subscribe announcement'}}]}]}  # check for text string
        msg = "You are now subscribed to announcements!"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'subscribe'}}]}]}  # check for text string
        msg = "Please specify what to subscribe to. Type 'help' or visit " \
               "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'subscribe TDT4100'}}]}]}  # check for text string
        msg = None
        response = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)


        test_text = {'entry': [{'messaging': [{'message': {'text': 'subscribe TDTPOTET'}}]}]}  # check for text string
        msg = None
        response = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)


        test_text = {'entry': [{'messaging': [{'message': {'text': 'unsubscribe'}}]}]}  # check for text string
        msg = "Please specify what to unsubscribe to. Type 'help' or visit " \
               "https://github.com/Folstad/TDT4140/wiki/Commands for a list of supported commands"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')


        test_text = {'entry': [{'messaging': [{'message': {'text': 'unsubscribe announcement'}}]}]}  # check for text string
        msg = "You are now unsubscribed from announcements!"
        response, response_type = replier.arbitrate(test_id,test_text)
        self.assertEqual(response,msg)
        self.assertEqual(response_type,'text')



























if __name__ == '__main__':
    unittest.main()
