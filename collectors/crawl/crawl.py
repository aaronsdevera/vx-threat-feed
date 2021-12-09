import time
import re
import uuid
import requests
from csv import writer

headers = {
    'user-agent': 'VX Underground Threat Feed https://vx-underground.org'
}

def get_response(TARGET_URL: str):
    return requests.get(TARGET_URL,headers=headers)

def get_html_source(REQUESTS_RESPONSE):
    return REQUESTS_RESPONSE.text

def get_response_headers(REQUESTS_RESPONSE):
    return REQUESTS_RESPONSE.headers

def get_lastmodified_header(RESPONSE_HEADERS):
    return RESPONSE_HEADERS['last-modified']

def extract_ipv4(RAW_TEXT: str):
    pattern = r'\b((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}\b'
    return re.findall(pattern, RAW_TEXT)

def extract_domain(RAW_TEXT: str):
    pattern = r'\b((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,63}\b'
    return re.findall(pattern, RAW_TEXT)

def extract_sha256(RAW_TEXT: str):
    pattern = r'\b[A-Fa-f0-9]{64}\b'
    return re.findall(pattern, RAW_TEXT)

def extract_md5(RAW_TEXT: str):
    pattern = r'/^[a-f0-9]{32}$/i'
    return re.findall(pattern, RAW_TEXT)

TARGET_URL = 'https://raw.githubusercontent.com/pan-unit42/iocs/master/Darkside/Darkside_IOCs.txt'

response = get_response(TARGET_URL)

HTML_SOURCE = get_html_source(response)
HEADERS = get_response_headers(response)
LAST_MODIFIED = ''
try:
    LAST_MODIFIED = get_lastmodified_header(HEADERS)
except:
    pass


ipv4_list = extract_ipv4(HTML_SOURCE)
domain_list = extract_domain(HTML_SOURCE)
sha256_list = extract_sha256(HTML_SOURCE)
md5_list = extract_md5(HTML_SOURCE)

APPEND_LIST = []

for sha256 in sha256_list:
    uid = str(uuid.uuid4())
    created_at = time.time()
    first_seen = created_at
    last_seen = created_at

    if LAST_MODIFIED != '':
        first_seen = LAST_MODIFIED
        last_seen = LAST_MODIFIED

    observable_type = 'sha256'
    observable = sha256
    references = str([TARGET_URL])
    tags = str([])

    APPEND_LIST.append(
        [uid,created_at,first_seen,last_seen,observable_type,observable,references,tags]
    )

with open('vxu-observables.csv', 'a') as f:
  
    # Pass this file object to csv.writer()
    # and get a writer object
    writer_object = writer(f)
  
    for row in APPEND_LIST:
        writer_object.writerow(row)
  
    #Close the file object
    f.close()
    