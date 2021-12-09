# collector: `crawl`

This collector should do the following:
* make HTTP GET request to a target URL
* scan raw text from response for observables
* append observables to `vxu-observables.csv`

## run this from the project root directory
like so:
```
python3 collectors/crawl/crawl.py
 ```