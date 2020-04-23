'''
Created on April 23, 2020
@author: Fabricio Flores
Description: Creates a program that takes data from Google Sheets spreadsheet
and tweets the interpreted data.
'''

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import tweepy


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = 'SPREADSHEET_ID'
SAMPLE_RANGE_NAME = 'RAW Scores!A2:E'

def get_tweets_helper(username):
    auth = tweepy.OAuthHandler("CONSUMER_KEY", 
        "CONSUMER_SECRET")
    auth.set_access_token("ACCESS_TOKEN", 
        "ACCESS_TOKEN_SECRET")
    api = tweepy.API(auth) 
    #Sets a high count of tweets to search through
    number_of_tweets = 1000
    #This retrieves 
    tweets = api.user_timeline(screen_name=username,count=number_of_tweets) 
    tmp=[]    
    # create array of tweet information: username,  
    # tweet id, date/time, text 
    tweets_for_array = [tweet.text for tweet in tweets] # CSV file created  
    for j in tweets_for_array: 
        # Appending tweets to the empty array tmp 
        tmp += [j]
    return tmp

def get_tweets():
    #reverses the order of the tweets of the twitter account @CastleBeatSaber0=
    allTweets = get_tweets_helper("CastleBeatSaber")[::-1]
    return allTweets

def googleSheets():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    arr = []
    if not values:
        print('No data found.')
    else:
        for row in values:
            arr += [[row[1], row[2], row[3], row[4]]]
        #print(arr)
    return arr

def findStartPoint():
    """This function finds the starting point of the google sheets spreadsheet that should start getting tweeted"""
    #This is the data values from the google sheets set
    arr = googleSheets()
    #This is the tweets from the twitter account
    allTweets = get_tweets()
    index = len(googleSheets())
    for i in range(0, len(arr)):
        status = (arr[i][0] + " scored " + arr[i][2] + " points on " + arr[i][1] + " with the "
            "following tag: " + arr[i][3])
        if status not in allTweets:
            index = i
            break
    return index

def makeTweet():
    arr = googleSheets()
    index = findStartPoint()

    auth = tweepy.OAuthHandler("CONSUMER_KEY", 
        "CONSUMER_SECRET")
    auth.set_access_token("ACCESS_TOKEN", 
        "ACCESS_TOKEN_SECRET")
    api = tweepy.API(auth, wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True)
    
    for j in range(index, len(arr)):
        #Create API object
        status = (arr[j][0] + " scored " + arr[j][2] + " points on " + arr[j][1] + " with the "
            "following tag: " + arr[j][3])
        print("This is a tweet being sent out: '" + status + "'")
        api.update_status(status)

def main():
    makeTweet()
    
if __name__ == '__main__':
    main()
