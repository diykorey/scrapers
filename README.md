# scrapers

## Djinni

Install scrapy

    pip install Scrapy
    
Check scrapy.cfg file, proper value **djinni** should be configured
Run scraper with command

    scrapy crawl djinnispider -o output.csv
    
    Where
        djinnispider - name of spider, also there is another spider for ilustrative purpose - loginspider
        output.csv - name of output file
[How to configure pycharm?](https://medium.com/@andriyandrunevchyn/run-scrapy-project-in-pycharm-af93caa543b4)



Here you can find scraper for djinni.co. It's useful in case you neeed to download data of your candidates and theirs CVs



#### 3-rd of August 2023 added scraper for
## Glassdoor

Check scrapy.cfg file, proper value **glassdoor** should be configured

Run scraper with command

    scrapy crawl glassdoor -o output.csv
    
    Where
        djinnispider - name of spider, also there is another spider for ilustrative purpose - loginspider
        output.csv - name of output file