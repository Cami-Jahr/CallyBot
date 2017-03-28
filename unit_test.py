import reply
import credentials


credential = credentials.Credentials()
replier = reply.Reply(credential.access_token)

def test_process_data():
    test_data_message={'entry':[{'messaging':[{'message':'this is message'}]}]} # check for message not text or attachment
    data_type, content = reply.Reply.process_data(test_data_message)
    assert data_type=="unknown" and content==""

    test_data_text={'entry':[{'messaging':[{'message':{'text':'this is text'}}]}]} # check for text string
    data_type, content = reply.Reply.process_data(test_data_text)
    assert data_type=="text" and content=="this is text"

    test_data_type={'entry':[{'messaging':[{'message':{'attachments':[{'type':'this is a type'}]}}]}]} # check for nonexistent type 
    data_type, content = reply.Reply.process_data(test_data_type)
    assert data_type=="unknown" and content==""

    test_data_image={'entry':[{'messaging':[{'message':{'attachments':[{'type':'image','payload':{'url':'this is image url'}}]}}]}]} # check for image
    data_type, content = reply.Reply.process_data(test_data_image)
    assert data_type=="image" and content=="this is image url"

    test_data_video={'entry':[{'messaging':[{'message':{'attachments':[{'type':'video','payload':{'url':'this is video url'}}]}}]}]} # check for video
    data_type, content = reply.Reply.process_data(test_data_video)
    assert data_type=="video" and content=="this is video url"

    test_data_file={'entry':[{'messaging':[{'message':{'attachments':[{'type':'file','payload':{'url':'this is file url'}}]}}]}]} # check for file
    data_type, content = reply.Reply.process_data(test_data_file)
    assert data_type=="file" and content=="this is file url"

    test_data_audio={'entry':[{'messaging':[{'message':{'attachments':[{'type':'audio','payload':{'url':'this is audio url'}}]}}]}]} # check for audio
    data_type, content = reply.Reply.process_data(test_data_audio)
    assert data_type=="audio" and content=="this is audio url"

    test_data_multimedia={'entry':[{'messaging':[{'message':{'attachments':[{'type':'multimedia','payload':'this is multimedia url'}]}}]}]} # check for multimedia
    data_type, content = reply.Reply.process_data(test_data_multimedia)
    assert data_type=="multimedia" and content=="this is multimedia url"

    test_data_geolocation={'entry':[{'messaging':[{'message':{'attachments':[{'type':'geolocation','payload':'this is geolocation url'}]}}]}]} # check for geolocation
    data_type, content = reply.Reply.process_data(test_data_geolocation)
    assert data_type=="geolocation" and content=="this is geolocation url"
