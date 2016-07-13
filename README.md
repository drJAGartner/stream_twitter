# stream_twitter
This twitter streamer is part of a multi-part process whereby a geo-bounding box is specified for scraping twitter data.
Once Tweets are pulled, a secondary script will identify those whose source is instagram, and we navigate to the webpage to find the
image url.  From there, instagram images are featurized, providing a robust source of information.

##Docker

```
# example docker commands:
docker build -t stream_twitter .
docker run -it --rm --name get_tweets -e "TWITTER_KEYS_FILE=./private/twitter_keys.json" stream_twitter
```

##Scripts
###stream_twitter.py
The primary script for getting data from the twitter 1% stream.  This file is fairly robust, and will cycle through a set of twitter
keys on a regular basis to avoid data throttling, and cuts new files every 5 minutes to allow downstream processes to itteratively
process data.
###extract_tweet_images.py
This script reads through the tweets, and in the instance that the tweet source is Instagram, will navigate to the page and retrieve the
image url from the metadata.  The original tweets will be rewritten, and in the case where instagram data is present, will be augmented
with a new 'instagram' field.

##Directory Structure
The system uses a series of folders and file system watching in order to insure each process can continues even if one process fails.
For all scripts, you must specify a base path where text files will be written.  The directories needed are:
###live_stream
This directory should only have a single file, which contains the actively pulled tweet data.
When a new file is cut (every 5 minutes), the previous file is moved to tweets_no_scraped_images
###tweets_no_scraped_images
This is where the scraper will move tweets when it cuts a new file.  The image url extractor will read
files from this directory.  Once it has done so, this script will remove the tweet files stored here.
###tweets_w_img_url
This is where the image extractor writes files.

