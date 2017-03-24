import requests


class ThreadSettings:
    def __init__(self, access_token):
        self.access_token = access_token

    def set_greeting(self, greeting):  # Set greeting text
        data = {
            "setting_type": "greeting",
            "greeting": {
                "text": greeting
            }
        }
        response = requests.post(self.get_thread_url(), json=data)
        print(response.content)

    def set_get_started(self):  # Set Get Started button
        data = {
            "setting_type": "call_to_actions",
            "thread_state": "new_thread",
            "call_to_actions": [{
                "payload": "start_new_chat"
            }]
        }
        response = requests.post(self.get_thread_url(), json=data)
        print(response.content)

    def set_persistent_menu(self):  # Set persistent menu
        data = {
            "setting_type": "call_to_actions",
            "thread_state": "existing_thread",
            "call_to_actions": [{
                "type": "postback",
                "title": "help",
                "payload": "help"},
                {
                    "type": "postback",
                    "title": "login",
                    "payload": "login"},
                {
                    "type": "postback",
                    "title": "get deadline(s)",
                    "payload": "get deadlines"},
            ]}
        response = requests.post(self.get_thread_url(), json=data)
        print(response.content)

    def whitelist(self, domains):  # Whitelist domains so it can be url'ed
        data = {
            "setting_type": "domain_whitelisting",
            "whitelisted_domains": [domains],
            "domain_action_type": "add"
        }
        response = requests.post(self.get_thread_url(), json=data)
        print(response.content)

    def get_thread_url(self):
        return "https://graph.facebook.com/v2.8/me/thread_settings?access_token=" + self.access_token
