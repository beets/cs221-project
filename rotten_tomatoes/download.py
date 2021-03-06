import errno
import json
import os
import time
import urllib
import subprocess
import sys

"""
Fetches movie data specifed in INPUT_TSV from Rotten Tomatoes.
Stores json data for each movie separately in DIR_NAME/<imdb_movie_id>.json
Requires some post-processing (for wrong and failed movie fetches).
"""

API_KEY = ''
QUERY_URL = 'http://api.rottentomatoes.com/api/public/v1.0/movies.json?'

INPUT_TSV = '../sql/dataset.tsv'

DIR_NAME = 'data_%s' % time.strftime('%Y%m%d-%H%M')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def fetch_data(dir_name, movie_id, title):
    params = {}
    params['apikey'] = API_KEY
    params['q'] = title
    params['page_limit'] = 1
    try:
        json_fetch = urllib.urlopen(QUERY_URL + urllib.urlencode(params))
        json_data = json.load(json_fetch)
        if not 'movies' in json_data or len(json_data['movies']) == 0:
            print 'No json_data fetched for (%s) "%s"' % (movie_id, title)
            return
        fetched_title = json_data['movies'][0]['title']
        out_filename = '%s.json' % (movie_id)
        json_dump = json.dumps(json_data, indent=4)

        if fetched_title.lower().find(title.lower()) != 0:
            #print 'Fetched wrong movie: %s instead of (%s) %s' % (fetched_title, movie_id, title)
            out_filename = 'wrong-' + out_filename
            json_dump = "imdb title: %s\n%s" % (title, json_dump)

        out = open('%s/%s' % (dir_name, out_filename), 'w')
        out.write(json_dump)
        out.close()
    except Exception as e:
        print "Unexpected error on %s: %s" % (movie_id, e)
    else:
        out.close()

def process_file():
    dataset = open(INPUT_TSV, 'r')
    cnt = 0
    for line in dataset:
        data = line.split('\t')
        if not data[0].isdigit():
            print "skipping %s" % line
            continue
        title = data[1]
        if title[0] == '"':
            title = title[1:]
        if title[-1] == '"':
            title = title[:-1]
        fetch_data(DIR_NAME, data[0], title)  # strip quotes
        if ++cnt % 50:
            time.sleep(2)

if __name__ == '__main__':
    # Unbuffered tee
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    tee = subprocess.Popen(["tee", "log.txt"], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())

    mkdir_p(DIR_NAME)
    print "Writing to %s" % DIR_NAME
    process_file()
