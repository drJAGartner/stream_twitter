import oauth2 as oauth
import urllib2 as urllib
import datetime, time, os, sys, json

def getCredentials():
    #you'll need to get these by registering for your own twitter developer account
    #i've created multiple access keys to loop through to avoid timeout
    dict_llaves = json.load(open("private/keyFile.json"))
    auth_info = []
    for llave in dict_llaves:
        api_key = llave["consumer_key"]
        api_secret = llave["consumer_secret"]
        access_token_key = llave["access_token"]
        access_token_secret = llave["access_secret"]
        oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
        oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)
        auth_info.append((oauth_token, oauth_consumer))
    return auth_info

def twitterreq(oauth_token, oauth_consumer, url, http_method, parameters):
    http_handler  = urllib.HTTPHandler(debuglevel=0)
    https_handler = urllib.HTTPSHandler(debuglevel=0)
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    req = oauth.Request.from_consumer_and_token(oauth_consumer, token=oauth_token, http_method=http_method, http_url=url, parameters=parameters)
    req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)
    headers = req.to_header()
    if http_method == "POST":
        encoded_post_data = req.to_postdata()
    else:
        encoded_post_data = None
    url = req.to_url()
    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)
    response = opener.open(url, encoded_post_data)
    return response

def stream_data(response, response_open_time, tweet_file_path):
    current_block = datetime.datetime.now()
    current_string = str(current_block.date())+"_"+str(current_block.time())+".json"
    out_file = open(tweet_file_path+"/live_stream/"+current_string, "w", 0)
    try:
        for line in response:
            now = datetime.datetime.now()
            print "response at", str(now)
            diff = now - current_block
            if diff.seconds > 180:
                out_file.close()
                response_up_time = now - response_open_time
                os.rename(tweet_file_path+"/live_stream/"+current_string, tweet_file_path+"/tweets_no_scraped_images/"+current_string)
                if response_up_time.seconds > 900:
                    return
                current_block = now
                print "\nNew File:", str(current_block)
                current_string = str(current_block.date())+"_"+str(current_block.time())+".json"
                out_file = open(tweet_file_path+"/live_stream/"+current_string, "w", 0)
                #every 2 hours, close existing connection, open under new key to avoid timeout
            try:
                json.load
                out_file.write(line.strip()+"\n")
                print ".",
            except:
                print "json load error:", sys.exc_info()[0]
                continue
    except:
        print "No response error"
        time.sleep(20)

def main(tweet_file_path):
    print "Start Streaming"
    auth_info = getCredentials()
    auth_counter = 0

    http_method = "GET"
    url = "https://stream.twitter.com/1.1/statuses/filter.json?stall_warnings=true&locations=-11.9591,49.637,2.8771,57.863"
    print "Using url", url
    pars = []
    response = twitterreq(auth_info[auth_counter][0], auth_info[auth_counter][1], url, http_method, pars)
    response_open_time = datetime.datetime.now()
    print "Response open time: ", str(response_open_time)

    while True:
        stream_data(response, response_open_time, tweet_file_path)
        response_open_time = datetime.datetime.now()
        print "New connection @", str(response_open_time)
        response.close()
        auth_counter = (auth_counter+1)%len(auth_info)
        response = twitterreq(auth_info[auth_counter][0], auth_info[auth_counter][1], url, http_method, pars)



if __name__ == '__main__':
    #tweet_file_path = '/Volumes/ed_00/data/raw_tweet_data'
    tweet_file_path = '/Users/jgartner/Desktop/raw_tweet_data'
    main(tweet_file_path)