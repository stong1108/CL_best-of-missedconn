# Best of Craigslist: Missed Connections

This repo contains Python code for scraping Best-Of-Craigslist's Missed Connections posts. Per the website, these posts have made the "best-of" list by reader nominations.

This scraper is based off of my original `CL_missedconn` scraper and has slight modifications due to Craigslist's "best of" posting format. For the original `CL_missedconn` scraper for an individual city's Missed Connections, see https://github.com/stong1108/CL_missedconn

### Contents
**MissedConn.py**<br>
Class file for a Best-Of-Craigslist's Missed Connections scraper object

```python
from BestOfMC import BestOfMC

mc = BestOfMC()
mc.get_df()
```

**bestofmc.pickle**<br>
Pickle object containing Pandas DataFrame of scraped Missed Connections from http://www.craigslist.org/about/best/all/mis (collected on 07/26/2016)

```python
import pandas as pd

df = pd.read_pickle('bestofmc.pickle')
```

***

**DataFrame Columns**

|Column|Data Type|Description|
|:---:|:---:|:---|
|`title`|str|title of Missed Connection post|
|`category`|str|string describing gender posting Missed Connection for ("4") another gender- m4w, m4m, w4m, w4w, or None|
|`post_dt`|datetime|timestamp of when post was created (or updated)|
|`post`|str|content of Missed Connection post that describes the interaction|
|`loc`|str|description of where Missed Connection occurred (if provided)|
|`url`|str|page url of Missed Connection post|
|`record_dt`|datetime|timestamp of when Missed Connection post was scraped|
|`city`|str|city that Missed Connection was posted under|
|`raw_page`|str|string of raw html of Missed Connection (unaltered data)|
|`has_pic`|int|1 if Missed Connection contained a picture, 0 if no picture|
