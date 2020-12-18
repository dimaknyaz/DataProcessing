from google_trans_new import google_translator  
import pandas as pd
translator = google_translator()  
# insert path here 
df=pd.read_csv(r"C:\Users\Dima\Downloads\JobData.csv")

jobTitles=[df['Job Title'][i] for i in range(len(df))]

jobDescribtions = [df['Job Description'][i] for i in range(len(df))]

translationsJobs=[]
translationsDescr=[]
# that's not the most efficient way in the world, but if I split it in chunks it will assume the entire translation/
# is one big string
for i in range(len(df)):
    print(7)
    tran = translator.translate(jobTitles[i], lang_src='nl', lang_tgt='en')
    translationsJobs.append(tran)
    descr= translator.translate(jobDescribtions[i], lang_src='nl', lang_tgt='en')
    #sometimes describtion is too long (but never above 10000 digits):
    if descr=='Warning: Can only detect less than 5000 characters':
        descr=''
        part1=translator.translate(jobDescribtions[i][0:4998], lang_src='nl', lang_tgt='en')
        part2=translator.translate(jobDescribtions[i][4999:], lang_src='nl', lang_tgt='en')
        descr=part1+part2
       
    translationsDescr.append(descr)

    
df['Job Title']=df['Job Title'].replace(jobTitles,translationsJobs)

tr=[translationsDescr[i].replace('\n'," ") for i in range(len(translationsDescr))]
df['Job Description']=df['Job Description'].replace(jobDescribtions,tr)

#insert where to save file here
df.to_csv(r"C:\Users\Dima\Downloads\JobDataTranslated.csv")
