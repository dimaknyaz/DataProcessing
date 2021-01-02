# DataProcessing
# All things in one sentence: we generate a huge list of all possible requirments and intersect it with all skills/requirments extracted for each vacancy

In order to run it, we might need to change location of chromedriver and paths to files. Here is a link to install chromedriver https://chromedriver.storage.googleapis.com/index.html?path=87.0.4280.88/

First, WebScrapper is a scrapper to collect 1000 vacancies from Glassdoor. Translator translates the vacancies from csv file and writes it in another csv file. Wods analysis 2 starts from translated data and ends with writing list of requirments for each vacancy (using excel files that can be found on drive)
Finally job matching and jon matching2 (more complete) create 2 final output using clustered criteria 

NLP files generate nice pictures and use k-means clustering to try to cluster jobs
