import os
import datetime
import pprint
import requests
import urlparse
import urllib
import re
import string
from lxml import html
from bs4 import BeautifulSoup
import time
import json
import sqlite3

sqlite_file = 'popular_tech.sqlite'

# clear terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

#creates a connection to sqlite3 
# db with name 'db_file' returns
# connection on success, None otherwise
def get_db_conn(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print('SQLITE3 DB ERROR: %s ' % e)
        return None


# insert data into sqlite db
# todo - insert everything at once
def db_add(term, category, city, state, country, date, num_jobs):
    sql = '''INSERT INTO POPULAR_TECH 
             VALUES (?,?,?,?,?,?,?,?)'''
# Connecting to the database file
    conn = get_db_conn(sqlite_file)
    c = conn.cursor()
    try:
        c.execute(sql, (None,term, category, city, state, country, date, num_jobs))

    except sqlite3.Error as e:
        print("SQLITE3 DB ERROR: %s " %e)

    conn.commit()
    conn.close()

# save search terms to file (json)
# requires a dict as a parameter
def save_terms(data):
    with open('terms.json', 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True, default=str)

# read search terms from file (json)
# returns a dict
def read_terms():
    with open('terms.json') as infile:
        data = json.loads(infile.read())
        return data

# create a dict from terms
def create_term_dict(jsn, term_dict):
    for category in jsn:
        term_dict[category] = {}
        for term in jsn[category]: 
            term_dict[category][term] = 0

# create a dict of dicts
# used when counting co-occurence of terms 
def create_dict_dict(term_dict, dict_dict):
    for term in term_dict: 
            term_dict[term] = [0,]

# create a list of terms
def create_term_list(jsn, term_list):
    for category in jsn:
        for term in jsn[category]: 
            term_list.append(term)

# extract job summary from page
# used when counting co-occurence of terms
def get_job_summary(soup): 
 summary = soup.find(name="span", attrs={"class":"summary", "id":"job_summary"})
 if summary is not None:
    return summary.text.lower()

# extract job titles from results page
# used when counting occurence of job titles
def get_job_titles(soup): 
 job_titles= []
 for div in soup.find_all(name="div", attrs={"class":"row"}):
     for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
         job_titles.append(a['title'].lower())
 return(job_titles)

def count_titles(title_list, title_dict):
    for title in title_list: 
        title = title.lower()
        if title in title_dict:
            title_dict[title] += 1
        else:
            title_dict[title] = 1
    return title_dict

# returns a list of urls to jobs
def get_job_links(soup): 
 job_links = []
 for div in soup.find_all(name="div", attrs={"class":"row"}):
     for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
         job_links.append(MAIN_URL +  a['href'])
 return(job_links)

# given a url, get the job id 
def get_job_id(url):
    job_id = str()
    try:
        parsed = urlparse.urlparse(url)
        params_dict = urlparse.parse_qs(parsed.query)
        job_id = params_dict['jk'][0]
    finally:
        return job_id

# find and return total number of jobs for given search
def get_job_ct(soup):
    pg_ct_div = soup.find(name="div", attrs={"id":"searchCount"})
    if pg_ct_div is not None:
        pg_ct_str = re.findall(r'\d*,*\d+',pg_ct_div.string)
        pg_ct_str = pg_ct_str[1].replace(",","")
        print pg_ct_str
        return int(pg_ct_str)
    else:
        return 0

def get_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    return soup

# note the occurence of search terms in a summary
def process_job_summary(job_summary, word_dict): 
  clear_screen()
  tmp = {}
  job_summary = job_summary.replace('-', ' ')
  job_summary = job_summary.replace('/', ' ')
  job_summary = job_summary.replace(',', ' ')
  job_summary = job_summary.replace('\\', ' ')
  job_summary = job_summary.replace('\\n', ' ')
  for word in job_summary.split():
    remove = string.punctuation + string.whitespace
    remove = remove.replace('+','')
    remove = remove.replace('#','')
    word = word.strip(remove) 
    word = word.lower()
    # only count each term once,
    # even if it appears multiple times on a page
    if word in word_dict:
        tmp[word] = True
  for t in tmp:
        word_dict[t] += 1
  #pp = pprint.PrettyPrinter(width=80)
  #pp.pprint(word_dict)
  print word_dict
  return word_dict

# processes page of results, list of links to summaries
def process_results_list(results_list, terms_dict):
    for job in results_list:
        sp = get_soup(job)
        s = get_job_summary(sp)
        if s is not None:
            process_job_summary(s, terms_dict)
    return terms_dict

# given a results page, count unique jobs
def count_unique_jobs(soup, id_dict):
    for l in get_job_links(soup):
        job_id = get_job_id(l)
        if job_id is not None:
            if job_id not in id_dict:
                id_dict[job_id] = 1
            else:
                id_dict[job_id] += 1
    return id_dict

start_time = datetime.datetime.now()
print start_time

JOBS_PER_PAGE = '50'
MAIN_URL = 'https://www.indeed.com'

terms_dict = {}
titles_dict = {}
id_dict = {}
create_term_dict(read_terms(), terms_dict) 

for category in terms_dict:
    for term in terms_dict[category]:
        CURRENT_TERM = term
        print CURRENT_TERM
        CURRENT_TERM = CURRENT_TERM.replace(' ','%2B' )
        CURRENT_TERM = CURRENT_TERM.replace('+','%2B' )
        CURRENT_TERM = CURRENT_TERM.replace('#','%23' )
        URL = ('https://www.indeed.com/jobs?as_and=&as_phr='
        + CURRENT_TERM +
        '&as_any=&as_not=&as_ttl=&as_cmp=&jt=all&st=&salary=&radius=100&l=Phoenix%2C+AZ&fromage=any&limit='
        + str(JOBS_PER_PAGE) +
        '&sort=&psf=advsrch')
        print URL
        soup = get_soup(URL)
        jobs_for_term = get_job_ct(soup)
        terms_dict[category][term] = jobs_for_term
        # add data to db, so we can track trends...
        db_add(term, category, 'phoenix', 'arizona', 'usa', start_time.strftime("%Y-%m-%d %H:%M"), jobs_for_term)
        # try to count unique jobs
        #count_unique_jobs(soup, id_dict)
        #for page in range(int(JOBS_PER_PAGE), jobs_for_term, int(JOBS_PER_PAGE)):
        #    URL = URL + '&start=' + str(page)
        #    soup = get_soup(URL)
        #    count_unique_jobs(soup, id_dict )

# add last run time
last_run_time = str(datetime.datetime.now())
terms_dict['last_run_time'] = last_run_time
with open('results.json', 'w') as outfile:
        json.dump(terms_dict, outfile, indent=4, sort_keys=False, default=str)
        #json.dump(terms_dict, outfile, indent=4, sort_keys=True, default=str)
#with open('job_id.json', 'w') as outfile:
#        json.dump(id_dict, outfile)

end_time = datetime.datetime.now()
elapsed_time = end_time - start_time
print 'elapsed time' 
print elapsed_time
