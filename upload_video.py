#!/usr/bin/env python

# Changes from sample provided here:
# https://github.com/youtube/api-samples/blob/master/python/upload_video.py
# - Modified get_authenticated_service() to store authentication token.
# - Build arguments directly without using argparser, per say.

import  argparse                           
import  http.client                        
import  httplib2                           
from    random                     import  random
from    time                       import  sleep
from    sys                        import  argv

import  google.oauth2.credentials          
import  google_auth_oauthlib.flow          
from    googleapiclient.discovery  import  build
from    googleapiclient.errors     import  HttpError
from    googleapiclient.http       import  MediaFileUpload

from    oauth2client.client        import  flow_from_clientsecrets
from    oauth2client.file          import  Storage
from    oauth2client.tools         import  run_flow

# from google_auth_oauthlib.flow import InstalledAppFlow
# import os


CLIENT_SECRETS_FILE    = 'client_secret.json'
# SCOPES                 = ['https://www.googleapis.com/auth/youtube.upload']
SCOPE                  = 'https://www.googleapis.com/auth/youtube.upload'
API_SERVICE_NAME       = 'youtube'
API_VERSION            = 'v3'
VALID_PRIVACY_STATUSES = ('public', 'private', 'unlisted')
httplib2.RETRIES       = 1
MAX_RETRIES            = 10
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS   = (httplib2.HttpLib2Error, IOError, http.client.NotConnected,
    http.client.IncompleteRead, http.client.ImproperConnectionState,
    http.client.CannotSendRequest, http.client.CannotSendHeader,
    http.client.ResponseNotReady, http.client.BadStatusLine)


def get_authenticated_service():
    storage = Storage('%s-oauth2.json' % argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(
            CLIENT_SECRETS_FILE,
            scope=SCOPE,
            message='WARNING: Please configure OAuth 2.0')
        # credentials = run_flow(flow, storage, args)
        credentials = run_flow(flow, storage)
    return build('youtube', 'v3', http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    tags = None
    if options['keywords']:
        tags = options['keywords'].split(',')
    body = dict(
        snippet = dict(
            title       = options['title'],
            description = options['description'],
            tags        = tags,
            categoryId  = options['category']
        ),
        status = dict(
            privacyStatus = options['privacyStatus']
        )
    )
    insert_request = youtube.videos().insert(
        part=','.join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(options['file'], chunksize=-1, resumable=True)
    )
    resumable_upload(insert_request)


def resumable_upload(request):
    response = None
    error    = None
    retry    = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' % response['id'])
                else:
                    exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e
        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit('No longer attempting to retry.')
            max_sleep = 2 ** retry
            sleep_seconds = random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            sleep(sleep_seconds)

