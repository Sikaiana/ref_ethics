import numpy as np
import pandas as pd
from requests import get
import os
import re
import json
import time


# 'doi_ethics' -> to scan list of DOIS
def doi_ethics(dois, save='yes'):
    res_ref_tot = []
    res_ref_ethic = []
    res_ref_ratio = []
    input_titles = []
    
    daf = pd.read_csv('DAFNEE.csv', sep=',')
    daf = daf['Journal'].tolist()  

    for doi in dois:
        # get metadata
        API_CALL = "https://opencitations.net/api/v1/metadata/" + doi
        HTTP_HEADERS = {"authorization": "72375271-8ca9-4b31-8c13-18d1b97fee4c"}
        res=get(API_CALL, headers=HTTP_HEADERS, timeout=10)

        #if res.text and not len(res.text) == 0 and res.status_code == 200:
        #if len(res.json()[0]["source_title"]) > 0:
        if res.status_code == 200 and len(res.json()) >= 1:
            """if answer ok"""
            # extract reference DOIS
            res_js = json.loads(res.text)[0]
            input_title = res_js['title']
            ref_dois = res_js['reference']
            ref_dois = ref_dois.split('; ')

            # get journal names of extracted refs, create list
            ref_names=[]
            for i in ref_dois:
                API_CALL = "https://opencitations.net/api/v1/metadata/" + i
                res_loop = get(API_CALL, headers=HTTP_HEADERS, timeout=10)

                if res_loop.status_code == 200 and len(res_loop.json()) >= 1:
                    """if answer ok"""
                    res_js_loop=res_loop.json()[0]["source_title"]
                    ref_names.append(res_js_loop)

                else:
                    """no info for ref or invalid DOI"""
                    ref_names.append(np.nan)

            # calculate #ethics, ratio
            ref_tot = len(ref_names)
            ref_ethic=len([value for value in ref_names if value in daf])
            ref_ratio = round(ref_ethic/ref_tot, 2)

        else:
            """no info for initial DOI or invalid DOI"""
            input_title = 'no info for this DOI, check if entered correctly'
            ref_tot = np.nan
            ref_ethic = np.nan
            ref_ratio = np.nan
        
        #bind to lists
        input_titles.append(input_title)
        res_ref_tot.append(ref_tot)
        res_ref_ethic.append(ref_ethic)
        res_ref_ratio.append(ref_ratio)

    myoutput = pd.DataFrame(np.column_stack([dois, res_ref_tot, res_ref_ethic, res_ref_ratio, input_titles]),
                                columns=['DOI', 'TotalRefs', 'Ethical', 'Ratio', 'Title'])

    if save == 'yes':
        ###check if res.csv already exists###
        savename = 'ethic_scan_' + (time.strftime("%Y-%m-%d_%H%M")) + '.csv'
        myoutput.to_csv(savename, index=False) 
    return myoutput


# 'txt_ethics' -> to scan .txt file of references
def txt_ethics(filename):
    #error if filename desn't contain '.txt.
    if os.path.isfile(filename) == True:
        # read ref file
        file = open(filename, 'r', encoding="utf8")
        content = file.read()
        content = content.lower() #turn everything into lower cases

        ref_dois = []
        with open(filename, 'r', encoding="utf8") as fd:
            for match in re.findall(r'(?:https://doi\.org/)\S*', fd.read()):
                ref_dois.append(match)
        #remove 'http...'
        ref_dois = [sub[16:] for sub in ref_dois]

        # get journal names of extracted refs, create list
        ref_names=[]
        for i in ref_dois:
            API_CALL = "https://opencitations.net/api/v1/metadata/" + i
            HTTP_HEADERS = {"authorization": "72375271-8ca9-4b31-8c13-18d1b97fee4c"}
            res_loop = get(API_CALL, headers=HTTP_HEADERS, timeout=10)

            if res_loop.status_code == 200 and len(res_loop.json()) >= 1:
                """if answer ok"""
                res_js_loop=res_loop.json()[0]["source_title"]
                ref_names.append(res_js_loop)

            else:
                """no info for ref or invalid DOI"""
                ref_names.append(np.nan)

        # import DAFNEE DB
        daf = pd.read_csv('DAFNEE.csv', sep=',')
        daf = daf['Journal'].tolist() 
        
        # calculate #ethics, ratio
        ref_true = [i for i in ref_names if i is not np.nan and i != '']
        ref_tot = len(ref_true)
        ref_ethic=len([value for value in ref_true if value in daf])
        ref_ratio = round(ref_ethic/ref_tot, 2)
        ref_nan = len(ref_names)-ref_tot

        print(ref_ethic, '/', ref_tot, 'references appear in ethic journals, thus a ratio of', ref_ratio,'!\n(', ref_nan, 'DOIs could not be identified.)')

    else:
        print('Invalid filename, the file does not exist!')
