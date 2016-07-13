import json, urllib2, os, time, argparse
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
            img_url = None
            if d0['source'].find('instagram') != -1:
                for d_url in d0['entities']['urls']:
                    try:
                        soup = url_to_soup(d_url['expanded_url'])
                        img_url = get_instagram_page_image(soup)
                        n_i += 1
                    except:
                        n_err += 1
            if img_url != None:
                print img_url
                f1.write(line[:-2]+', "instagram":{"img_url":"'+img_url+'"}'+line[-2:])
            else:
                f1.write(line)
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
    while n_sleep<60:
        if len(os.listdir(tweet_file_path+'/tweets_no_scraped_images/')) > 0:
            n_sleep = 0
            files = sorted(os.listdir(tweet_file_path+'/tweets_no_scraped_images/'), key=lambda x: os.stat(os.path.join(tweet_file_path+'/tweets_no_scraped_images/', x)).st_mtime)
            for s_file in files:
                t_out = time.time()
                if debug:
                    print "Processing file:", s_file
                get_file_images(tweet_file_path, s_file, debug=debug)
                try:
                    os.remove(tweet_file_path +'/tweets_no_scraped_images/' + s_file)
                except:
                    print "Error deleting file: " + tweet_file_path +'/tweets_no_scraped_images/' + s_file
                if debug:
                    print "Finished in", time.time() - t_out, "seconds "
        else:
            time.sleep(300)
            n_sleep += 1
            if n_sleep > 5:
                print "There have been no files to analyze for", n_sleep*5, "minutes, the twitter stream may be down"
    print "No new files for 3 hours, shutting down."



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", help="Directory where tweet files will be written locally", default="./downloads")
    parser.add_argument("--debug", help="Verbose Screen output for debugging", type=bool, default=False)
    args = parser.parse_args()
    tweet_file_path = args.outdir
    debug = args.debug
    main(tweet_file_path, debug = debug)
