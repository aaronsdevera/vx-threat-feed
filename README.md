# vx-threat-feed
VX Underground threat feed of indicators and observables

## Example row level schema
|Name|Description|Data Type|Format|
|---|---|---|---|
id|Unique row identifier|uuid|uuid
created_at|Timestamp of row creation|timestamp with time zone|timestamptz
type|Type of observable (`ipv4`,`sha256`,`md5`,`host`,`url`)|character varying|varchar
observable|Raw text of the observable|character varying|varchar	
references|Links to research or URL where observable is identified|ARRAY|_varchar	
tags|User submitted tags for observable (eg. `emotet`,`apt28`)|ARRAY|_varchar	
```

## TODO
* the discord collector is set to log to Elasticsearch. Let's rip that out
* discord collector needs to output same format as web crawl

## `.secrets`
Use a `.secrets` to stored anything sensitive. It is not tracked by git.