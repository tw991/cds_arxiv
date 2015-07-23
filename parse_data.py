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



def read_name_list(file):
    data = pd.read_csv(file)
    data = data.iloc[:10]
    firstname = data['First Name']
    lastname = data['Last Name']
    return firstname, lastname

def create_contributor_col(dataframe):
    data = dataframe
    for i in range(100):
        col_name = 'Contributor_%d' % i
        data[col_name] = ''
        return data

def main():
    firstname_list, lastname_list = read_name_list('./data-scientists.csv')
    first_initial_list = firstname_list.map(get_initial_query)
    data = pd.DataFrame(columns=['First Name', 'Last Name', 'Query_text', 'Arxiv-id', 'Time', 'Subject', 'Count', 'Inst_Count', 'Raw_Count'])
    #data = create_contributor_col(data)
    for i in range(len(first_initial_list)):
        firstname = firstname_list.iloc[i]
        first_initial = first_initial_list.iloc[i]
        lastname = lastname_list.iloc[i]
        initial_query = create_name_query(first_initial, lastname)
        name_query = create_name_query(firstname, lastname)
        query = arxiv(initial_query)
        query.parse()
        if query.count > 500:
            query = arxiv(name_query)
            query.parse()
            print('Warning: Initial query returns more than 500 papers. Use firstname query instead.')
        raw_count = query.count
        query.institution_verify(save=True)
        inst_count = query.count
        query = subject_verify(query)
        count = query.count
        for j in range(query.count):
            count_contributor = 0
            save_dict = {}
            save_dict['First Name'] = firstname
            save_dict['Last Name'] = lastname
            save_dict['Query_text'] = query.author
            save_dict['Arxiv_id'] = query.arxiv_id[j]
            save_dict['Time'] = query.time[j]
            save_dict['Subject'] = query.category[j]
            save_dict['Count'] = count
            save_dict['Inst_Count'] = inst_count
            save_dict['Raw_Count'] = raw_count
            for coauthor in query.contributor[j]:
                col_author = 'Contributor_%d' % count_contributor
                save_dict[col_author] = coauthor
                count_contributor += 1
                if count_contributor > 99:
                    break
            data = data.append(save_dict, ignore_index=True)
        data.to_csv('./out.csv',encoding='utf-8')





if __name__ == '__main__':
    main()