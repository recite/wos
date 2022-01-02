# WoS Scraper

### Workflow

1. [Get Control Group Articles](scripts/01_get_control_articles.py):
    
    - Iterates over [retracted articles](data/new_retracted_articles.csv) and get the day (PD), month (PD), year (PY), and research area (WC). 
    
    - Creates a query string of the following format:

    ```
    (SO=({SO})) AND 
       DOP=(YYYY-MM-DD/YYYY-MM-DD) AND 
       DT=(Article) AND 
       WC=({WC})
    ```

    Notes:
        * Constructs DOP from PD and PY
            * DOP ranges from start of the month to the end of the month when the day is not present. e.g, 2005-01-01/2005-01-31
            * When the day is present, e.g., 2005-01-21/2005-01-21 
        * DT is always the same

        * Sample final search string:

        ```
        (SO=(Science)) AND 
           DOP=(2005-01-21/2005-01-21) AND 
           DT=(Article) AND 
           WC=(Multidisciplinary Sciences)
        ```

    - Goes to www.webofscience.com and clicks on advanced search and parameters and enters the query string

    - Selects "full record" and exports all the search results. Save the file as search_results/rowid.xls where rowid is the rowid of the [retracted articles](data/new_retracted_articles.csv) being queried.

2. [Choose two records at random](scripts/02_choose_records_at_random.py) 

    Selects two records at random from the search results. And then save them to a separate file (selected_records.csv) along with the rowid column. (Results from each query will be concatenated to selected_records.csv) 

3. [Get citing articles](scripts/03_get_citing_articles.py)
    
    For each of the two records:
    * Searches for the title (TI), e.g., ```TI=(Mathematical modeling of planar cell polarity to understand domineering nonautonomy)```
    * Clicks on the records citations
    * Exports all the citations as tab delimited files (citing_articles/rowid_1.tsv and citing_articles/rowid_2.tsv)

# Requirements

1. Python 3 and selenium 
2. Chrome (version 92 or newer)
3. Make sure the chromedriver.exe (download it from https://sites.google.com/chromium.org/driver/) is at the same path as the main script while running

