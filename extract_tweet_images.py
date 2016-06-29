import json, urllib, urllib2, os,time
from bs4 import BeautifulSoup

def url_to_soup(url):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
   'Accept-Encoding': 'none',
   'Accept-Language': 'en-US,en;q=0.8',
   'Connection': 'keep-alive'}
    req = urllib2.Request(url,headers=hdr)
    response = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(req)
    return BeautifulSoup(response.read(), "html.parser")

def get_instagram_page_image(tweet_file_path, soup, s_id):
    l_meta = soup.head.find_all('meta')
    for m in l_meta:
        if m.has_attr('content'):
            ind = m['content'].find('jpg')
            if ind != -1:
                urllib.urlretrieve(m['content'][:ind+3], tweet_file_path+"/images/"+s_id+".jpg")

def get_file_images(tweet_file_path, s_file, debug=False):
    f0 = open(tweet_file_path + '/tweets_no_scraped_images/' + s_file, 'r')
    n_i, n_t, n_err = 0, 0, 0
    for line in f0:
        try:
            d0 = json.loads(line)
            s_id = d0['id_str']
            if 'media' in d0['entities']:
                d_m = d0['entities']['media']
                try:
                    urllib.urlretrieve(d_m[0]['media_url_https'], tweet_file_path+"/images/"+s_id+".jpg")
                    n_t += 1
                except:
                    continue

            if d0['source'].find('instagram') != -1:
                for d_url in d0['entities']['urls']:
                    try:
                        soup = url_to_soup(d_url['expanded_url'])
                        get_instagram_page_image(tweet_file_path, soup, s_id)
                        n_i += 1
                    except:
                        n_err += 1
                        continue
        except:
            print json.dumps(line)
            break

    if debug:
        print 'Errors:', n_err
        print 'Images from twitter:', n_t
        print 'Images from instagram:', n_i

def main(tweet_file_path, debug=False):
    n_sleep = 0
    while n_sleep<5:
        if len(os.listdir(tweet_file_path+'/tweets_no_scraped_images/')) > 0:
            files = sorted(os.listdir(tweet_file_path+'/tweets_no_scraped_images/'), key=lambda x: os.stat(os.path.join(tweet_file_path+'/tweets_no_scraped_images/', x)).st_mtime)
            for s_file in files:
                if s_file in ["analyzed", "live_stream"]:
                    continue
                t_out = time.time()
                if debug:
                    print "Processing file:", s_file
                get_file_images(tweet_file_path, s_file, debug=debug)
                os.rename(tweet_file_path +'/tweets_no_scraped_images/' + s_file, tweet_file_path + '/tweets_w_scraped_images/' + s_file)
                if debug:
                    print "Finished in", time.time() - t_out, "seconds "
        else:
            time.sleep(300)
            n_sleep += 1
    print "No more files to analyze, program terminating"

if __name__ == '__main__':
    #tweet_file_path = '/Volumes/ed_00/data/raw_tweet_data'
    tweet_file_path = '/Users/jgartner/Desktop/raw_tweet_data'
    main(tweet_file_path, debug=True)