# Importing all necessary libraries 
import cv2
import os
from os import listdir
from os.path import isfile, join
from pymongo import MongoClient
import pytesseract
import speech_recognition as sr
import moviepy.editor as mp
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

def getFilesPath(directory):
    return [f for f in listdir(directory) if isfile(join(directory, f))]

def getVideoFrames(video, videoPath, storieName):
    # Read the video from specified path 
    cam = cv2.VideoCapture(video) 

    # frame 
    currentframe = 0
    while(True): 
        
        # reading from frame 
        ret,frame = cam.read() 
        if ret: 
            # increasing counter so that it will 
            # show how many frames are created 
            currentframe += 1
            if currentframe > 25:
                # if video is still left continue creating images 
                name = videoPath + '/' + storieName.split('.')[0] + '.jpg'
                print ('Creating...' + name) 

                # writing the extracted images 
                cv2.imwrite(name, frame) 
                break
        else: 
            break

    # Release all space and windows once done 
    cam.release() 
    cv2.destroyAllWindows()

def getTextFromImage(imgPath):
    print('file: ' + imgPath)
    frame = cv2.imread(imgPath)
    scale_percent = 200 # percent of original size
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    img = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
    text = pytesseract.image_to_string(img, config='-c load_freq_dawg=0 load_system_dawg=0')
    print(text)
    return text

def getTextFromVideo(videoPath, storieName):
    # print('tiene audio? '+os.system('ffprobe -i '+videoPath+'/'+storieName+' -show_streams -select_streams a -loglevel error'))
    # command2mp3 = 'ffmpeg -i '+videoPath+'/'+storieName+' '+videoPath+'/'+storieName.split('.')[0]+'.mp3'
    # command2wav = 'ffmpeg -i '+videoPath+'/'+storieName.split('.')[0]+'.mp3 '+videoPath+'/'+storieName.split('.')[0]+'.wav'
    # os.system(command2mp3)
    # os.system(command2wav)
    r = sr.Recognizer()
    print('video: '+videoPath+'/'+storieName.split('.')[0]+'.mp4')
    clip = mp.VideoFileClip(videoPath+'/'+storieName.split('.')[0]+'.mp4')
    print('clip: '+str(clip))
    print('Audio: '+videoPath+'/'+storieName.split('.')[0]+'.wav')
    hasAudio = True
    try:
        clip.audio.write_audiofile(videoPath+'/'+storieName.split('.')[0]+'.wav')
    except:
        print('Error when converting video to audio, does the video has any audio?')
        hasAudio = False
    if hasAudio:
        with sr.AudioFile(videoPath+'/'+storieName.split('.')[0]+'.wav') as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio, language="es-ES")
                print(text)
                return text
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio, trying with english")
                try:
                    text = r.recognize_google(audio, language="en-EN")
                    print(text)
                    return text
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio :(")
                except sr.RequestError as e:
                    print("Could not request results from Google Speech Recognition service; {0}".format(e))
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

def saveToMongo(storie):
    client = MongoClient('localhost', 27017)
    database = client.InstacupData
    data = database['data']
    print(data.find({"storieId": storie['storieId']}).count())
    if data.find({"storieId": storie['storieId']}).count() == 0:
        data.insert(storie)
    else:
        if storie['storieImageText'] != '':
            data.update_one({"storieId": storie['storieId']}, {"$set": {"storieImageText": storie['storieImageText']}})
        else:
            data.update_one({"storieId": storie['storieId']}, {"$set": {"storieVideoText": storie['storieVideoText']}})


def main():
    dataToSave = {
        "user": '',
        "storieId": '',
        "isVideo": False,
        "storieImageText": '',
        "storieVideoText": '',
        "hasCode": False
    }
    storiesData = []
    print(dataToSave)
    os.system('python3 instabot.py -b users.txt')
    users = listdir('stories')
    for user in users:
        userStories = getFilesPath('stories/'+user)
        for userStorie in userStories:
            if userStorie.split('.')[1] == 'mp4':
                getVideoFrames('stories/'+user+'/'+userStorie, 'stories/'+user, userStorie)
    for user in users:
        userStories = getFilesPath('stories/'+user)
        dataToSave['user'] = user
        for userStorie in userStories:
            dataToSave['storieId'] = userStorie.split('.')[0]
            if userStorie.split('.')[1] == 'jpg':
                text = getTextFromImage('stories/'+user+'/'+userStorie)
                dataToSave['isVideo'] = False
                dataToSave['storieImageText'] = text
            else:
                text = getTextFromVideo('stories/'+user, userStorie)
                dataToSave['isVideo'] = True
                dataToSave['storieVideoText'] = text
            
            print('Texto de la imagen: ' + dataToSave["storieImageText"] if dataToSave["storieImageText"] is not None else "Nada :(")
            print('Texto del video: ' + dataToSave["storieVideoText"] if dataToSave["storieVideoText"] is not None else "Nada :(")
            isCode = input('Tiene esta historia un codigo? (Y/N)')
            if isCode == 'Y' or isCode == 'y':
                dataToSave["hasCode"] = True
            else:
                dataToSave["hasCode"] = False
            print(dataToSave)
            saveToMongo(dataToSave)
            storiesData.append(dataToSave)
            dataToSave = {
                "user": user,
                "storieId": '',
                "isVideo": False,
                "storieImageText": '',
                "storieVideoText": '',
                "hasCode": False
            }
    # train, test, train_labels, test_labels = train_test_split(storiesData,storiesData['hasCode'],test_size = 0.40, random_state = 42)
    # gnb = GaussianNB()
    # model = gnb.fit(train, train_labels)
    # preds = gnb.predict(test)
    # print(preds)
    # print(accuracy_score(test_labels,preds))
            
    

if __name__ == '__main__':
    main()
