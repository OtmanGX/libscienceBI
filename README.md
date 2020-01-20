# libscienceBI
Data Collection by scrapy from some IEE, ScienceDirect and ACM

Run docker with root privileges :

```
docker run -p 8050:8050 scrapinghub/splash
```
After that you can run the spider (iee or sd) :
```
scrapy crawl sd -a keywords="big data"
```
