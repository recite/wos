#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import os
from glob import glob

DOWNLOAD_PATH = './search_results'

print("Reading search results...")
df_list = []
for fn in glob(DOWNLOAD_PATH + '/*.xls'):
    df = pd.read_excel(fn)
    name = os.path.splitext(os.path.basename(fn))[0]
    df['ref_col'] = name
    df['name_each_file'] = df['ref_col'] + '_' + df.index.astype(str)
    df_list.append(df)

adf = pd.concat(df_list)

del adf['Unnamed: 57']
adf.columns

adf.reset_index(drop=True, inplace=True)
print('Number of articles from search results:', len(adf))

idf = pd.read_csv('retracted_articles.csv.gz')
print('Number of articles in the input data:', len(idf))

adf.drop(adf[adf['UT (Unique ID)'].isin(idf.UT)].index, inplace=True)
print('Number of articles after take out the articles in the input data:',
      len(adf))

sdf = adf.groupby('ref_col', group_keys=False).apply(lambda x:
                                                     x.sample(min(len(x), 2),
                                                              random_state=1))
print('Number of articles after sampling by 2:', len(sdf))

print('Save the selected records to file...')
sdf.ref_col = sdf.ref_col.astype(int)
sdf.sort_values('ref_col', inplace=True)
sdf.to_csv('selected_records.csv', index=False)
