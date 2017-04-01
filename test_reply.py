import reply
import credentials
import unittest

credential = credentials.Credentials()
replier = reply.Reply(credential.access_token)


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


if __name__ == '__main__':
    unittest.main()
