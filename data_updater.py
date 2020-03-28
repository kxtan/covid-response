import requests
import pandas as pd

def download_data(url):
    r = requests.get(url, 'data/data_in_excel.xlsx')

    with open('data/data_in_excel.xlsx', 'wb') as f:
        f.write(r.content)

def convert_excel_to_csv(infile, outfile):
    excel_file = pd.read_excel(infile)
    excel_file.to_csv(outfile, index=None, header=True)

# if __name__ == '__main__':
#     download_data('https://www.bsg.ox.ac.uk/sites/default/files/OxCGRT_Download_latest_data.xlsx')
#     convert_excel_to_csv('data/data_in_excel.xlsx', 'data/from_excel.csv')
