import pandas as pd
from parse_arxiv import *

def create_name_query(firstname, lastname):
    name_query = lastname + '_' + firstname
    return name_query

def sub_main():
    data = pd.read_csv('./data-scientists.csv')
    data = data.loc[:6]
    data['arxiv_count'] = 0
    data['Initial'] = ''
    data['Subject'] = ''
    for i in pyprind.prog_bar(range(len(data))):
        data.loc[i, 'Initial'] = get_initial_query(data.loc[i, 'First Name'])
        author = data.loc[i]
        initial_query = create_name_query(author['Initial'], author['Last Name'])
        name_query = create_name_query(author['First Name'], author['Last Name'])
        query = arxiv(name_query)
        query.parse()
        if query.count != 0:
            query.verify()
        data.loc[i, 'arxiv_count'] = query.count
    print data
    data.to_csv('./data-scientists-arxiv.csv')

def get_initial_query(firstname):
    return firstname[0]

def combine_subject(sub_list):
    out_set = []
    for lst in sub_list:
        out_set = list(set(out_set + lst))
    return out_set

if __name__ == '__main__':
    sub_main()