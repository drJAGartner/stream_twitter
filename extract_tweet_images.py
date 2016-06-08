import json, urllib, urllib2, os
from bs4 import BeautifulSoup
import time

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

def get_instagram_page_image(soup, s_id):
    l_meta = soup.head.find_all('meta')
    for m in l_meta:
        if m.has_attr('content'):
            ind = m['content'].find('jpg')
            if ind != -1:
                urllib.urlretrieve(m['content'][:ind+3], "/Volumes/ed_00/data/raw_tweet_data/images/"+s_id+".jpg")

def get_file_images(s_file, debug=False):
    f0 = open(s_file, 'r')
    i = 0
    t0 = time.time()
    n_i, n_t, n_err = 0, 0, 0
    for line in f0:
        i += 1
        try:
            d0 = json.loads(line)
            s_id = d0['id_str']
            if 'media' in d0['entities']:
                d_m = d0['entities']['media']
                try:
                    urllib.urlretrieve(d_m[0]['media_url_https'], "/Volumes/ed_00/data/raw_tweet_data/images/"+s_id+".jpg")
                    n_t += 1
                except:
                    continue

            if d0['source'].find('instagram') != -1:
                for d_url in d0['entities']['urls']:
                    try:
                        soup = url_to_soup(d_url['expanded_url'])
                        get_instagram_page_image(soup, s_id)
                        n_i += 1
                    except:
                        n_err += 1
                        continue
        except:
            print i
            print json.dumps(line)
            break

    if debug:
        print 'Errors:', n_err
        print 'Images from twitter:', n_t
        print 'Images from instagram:', n_i
        print 'Total Time: ', time.time() - t0

def main(tweet_file_path, debug=False):
    files = sorted(os.listdir(tweet_file_path), key=lambda x: os.stat(os.path.join(tweet_file_path, x)).st_mtime)
    for file in files:
        if file in ["analyzed", "live_stream"]:
            continue
        if debug:
            print "Processing file:", file
        get_file_images(tweet_file_path +'/'+file)
        os.rename(tweet_file_path + "/" + file, tweet_file_path + "/analyzed/" + file)

if __name__ == '__main__':
    main()