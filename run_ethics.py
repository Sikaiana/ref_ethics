#Download the functions ('ethics_functions.py') and the dafnee database (DAFNEE.csv)

from ethics_functions import *

### To scan a list of DOIs
# create a list of DOIs to check
dois=['10.1091/mbc.E19-03-0147', '10.1016/j.tree.2018.02.005']

#'save' species wether to save the output table ('yes'/'no'; default save='yes')
res = calc_ethics(dois, save='yes')
print(res)

### To scan a .txt file (make sure your copied references contain complete DOIs):
txt_ethics('test_refs.txt')
