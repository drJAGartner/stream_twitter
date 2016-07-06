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

def get_instagram_page_image(soup):
    l_meta = soup.head.find_all('meta')
    for m in l_meta:
        if m.has_attr('content'):
            ind = m['content'].find('jpg')
            if ind != -1:
                return m['content'][:ind+3]
    return None

def get_file_images(tweet_file_path, s_file, debug=False):
    f0 = open(tweet_file_path + '/tweets_no_scraped_images/' + s_file, 'r')
    f1 = open(tweet_file_path + '/tweets_w_img_url/' + s_file, 'w')
    n_i, n_t, n_err = 0, 0, 0
    for line in f0:
        try:
            d0 = json.loads(line)
            # if 'media' in d0['entities']:
            #     d_m = d0['entities']['media']
            #     try:
            #         urllib.urlretrieve(d_m[0]['media_url_https'], tweet_file_path+"/images/"+s_id+".jpg")
            #         n_t += 1
            #     except:
            #         continue
            img_url = None
            if d0['source'].find('instagram') != -1:
                for d_url in d0['entities']['urls']:
                    try:
                        soup = url_to_soup(d_url['expanded_url'])
                        img_url = get_instagram_page_image(soup)
                        if img_url is not None:
                            d0['instagram'] = {'img_url':img_url}
                        n_i += 1
                    except:
                        n_err += 1

            if d0['source'].find('instagram') != -1:
                print "Key check:",
                print 'instagram' in d0.keys()
            f1.write(json.dumps(d0) + "\n")
        except:
            print json.dumps(line)
            break
    f1.close()
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
                t_out = time.time()
                if debug:
                    print "Processing file:", s_file
                get_file_images(tweet_file_path, s_file, debug=debug)
                #os.rename(tweet_file_path +'/tweets_no_scraped_images/' + s_file, tweet_file_path + '/tweets_w_scraped_images/' + s_file)
                os.remove(tweet_file_path +'/tweets_no_scraped_images/' + s_file)
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