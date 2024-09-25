# getFamaFrenchFactors.py
# Author: Vash
# Modified by Valentyn Panchenko
# Version 0.0.6
# Last updated: 27 October 2023

"""
This programme gets cleaned versions of factors including:
    * famaFrench3Factor() -- Fama French 3 factor (MRP, SMB, HML)
    * momentumFactor() -- Momentum (MOM)
    * carhart4Factor() -- Carhart 4 factors (MRP, SMB, HML, MOM)
    * famaFrench5Factor() -- Fama French 5 factors (MRP, SMB, HML, RMW, CMA)

The frequency of the data is controlled by a single parameter
frequency take values:
'd' daily (default)
'm' monthly
'a' annual


Updates in Version 0.0.6:
Adds support for daily data in addition to annual and monthly data
DataFrame "date_ff_factors" field changed to more conventional "Date"
"Date" is harmonised to Pandas date format set to the last day the period (for monthly and annual series)

Updates in Version 0.0.4:
Replaces manual URL with scraped URL for initial futureproofing.

Updates in Version 0.0.3:
Adds support for annual data in addition to monthly data.
"""

import pandas as pd
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup

# Extract URLs to download
url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

text_to_search = ['Fama/French 3 Factors', 'Momentum Factor (Mom)']
all_factors_text = soup.findAll('b', string=text_to_search)

home_url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/"
all_factor_links = []
for text in all_factors_text:
    links_for_factor = []  # Stores all links for a factor
    for sib in text.next_siblings:  # Find next element
        # URLs are stored in bold tags, hence...
        if sib.name == 'b':
            bold_tags = sib
            try:
                link = bold_tags.find('a')['href']
                links_for_factor.append(link)
            except TypeError:
                pass
    csv_links = [home_url + link for link in links_for_factor if 'csv' in link.lower()]
    txt_links = [home_url + link for link in links_for_factor if 'txt' in link.lower()]
    factor_dict = {'factor' : text, 'csv_links' : csv_links, 'txt_links' : txt_links}
    all_factor_links.append(factor_dict)

ff_factor_dict = dict(all_factor_links[0])
momAndOthers_dict = dict(all_factor_links[1])


def famaFrench3Factor(frequency='d'):
    '''
    Returns Fama French 3 factors (Market Risk Premium, SMB, HML)

    Set frequency as:
        'd' for daily factors
        'm' for monthly factors
        'a' for annual factors

    '''
    rows_to_skip = 3

    if frequency == 'd':
        ff3_raw_data = ff_factor_dict['csv_links'][2]
        ff3_factors = pd.read_csv(ff3_raw_data, skiprows=rows_to_skip)
        ff3_factors.rename(columns={ff3_factors.columns[0]: 'Date'},
                           inplace=True)
        # Ignore copyright footer     
        ff3_factors = ff3_factors.iloc[:-2]
        ff3_factors['Date'] = pd.to_datetime(ff3_factors['Date'],
                                                    format='%Y%m%d')
    else:
        ff3_raw_data = ff_factor_dict['csv_links'][0]
        ff3_factors = pd.read_csv(ff3_raw_data, skiprows=rows_to_skip)
        ff3_factors.rename(columns={ff3_factors.columns[0]: 'Date'},
                           inplace=True)
        
        # Clean annual and monthly versions

        # Get index of annual factor returns
        annual_factor_index_loc = ff3_factors[
            ff3_factors.values == ' Annual Factors: January-December '].index

        if frequency == 'm':
            ff3_factors.drop(ff3_factors.index[annual_factor_index_loc[0]:], inplace=True)

            # Convert dates to pd datetime objects
            ff3_factors['Date'] = pd.to_datetime(ff3_factors['Date'],
                                                            format='%Y%m')
            # Shift dates to end of month
            ff3_factors['Date'] = ff3_factors['Date'].apply(
                lambda date : date + relativedelta(day = 1, months = +1, days = -1))

        elif frequency == 'a':
            # Extract annual data only
            ff3_factors.drop(ff3_factors.index[:annual_factor_index_loc[0]],
                             inplace=True)

            # Ignore copyright footer & first 2 header rows
            ff3_factors = ff3_factors.iloc[2:-1]
            ff3_factors.reset_index(inplace=True)
            ff3_factors.drop(columns=ff3_factors.columns[0], inplace=True)

            # Deal with spacing issues (e.g. '  1927' instead of '1927')
            ff3_factors['Date'] = ff3_factors['Date'].apply(
                lambda x : x.strip())

            # Convert dates to datetime objects
            ff3_factors['Date'] = pd.to_datetime({ff3_factors['Date']}+"1231",
                                                            format='%Y%m%d')


    # Convert all factors to numeric and decimals (%)
    for col in ff3_factors.columns[1:]:
        ff3_factors[col] = pd.to_numeric(ff3_factors[col]) / 100

    return ff3_factors


def momentumFactor(frequency='d'):
    '''
    Returns the Momentum factor

    Set frequency as:
        'd' for daily factors
        'm' for monthly factors
        'a' for annual factors

    '''
    rows_to_skip = 13

    if frequency == 'd':
        mom_raw_data = momAndOthers_dict['csv_links'][1]
        mom_factor = pd.read_csv(mom_raw_data, skiprows=rows_to_skip)
        mom_factor.rename(columns = {mom_factor.columns[0] : 'Date'},
                          inplace=True)
        # Ignore copyright footer
        mom_factor = mom_factor.iloc[:-2]
        mom_factor['Date'] = pd.to_datetime(mom_factor['Date'],
                                                    format='%Y%m%d')
    else:
        mom_raw_data = momAndOthers_dict['csv_links'][0]

        mom_factor = pd.read_csv(mom_raw_data, skiprows=rows_to_skip)
        mom_factor.rename(columns = {mom_factor.columns[0] : 'Date'},
                          inplace=True)

        # Get index of annual factor returns
        annual_factor_index_loc = mom_factor[
                mom_factor.values == 'Annual Factors:'].index
        # Clean annual and monthly versions
        if frequency == 'm':
            # Exclude annual factor returns
            mom_factor.drop(mom_factor.index[annual_factor_index_loc[0]:], inplace=True)

            # Convert dates to pd datetime objects
            mom_factor['Date'] = pd.to_datetime(mom_factor['Date'],
                                                           format='%Y%m')

            # Shift dates to end of month
            mom_factor['Date'] = mom_factor['Date'].apply(
                lambda date : date + relativedelta(day = 1, months = +1, days = -1))

        elif frequency == 'a':
            # Extract annual data only
            mom_factor.drop(mom_factor.index[:annual_factor_index_loc[0]],
                            inplace=True)

            # Ignore copyright footer & first 2 header rows
            mom_factor = mom_factor.iloc[3:-1]
            mom_factor.reset_index(inplace=True)
            mom_factor.drop(columns=mom_factor.columns[0], inplace=True)

            # Deal with spacing issues (e.g. '  1927' instead of '1927')
            mom_factor['Date'] = mom_factor['Date'].apply(
                lambda x : x.strip())

        # Convert dates to datetime objects
        mom_factor['Date'] = pd.to_datetime(mom_factor['Date']+"1231",
                                                       format='%Y%m%d')

    # Convert all factors to numeric and decimals (%)
    for col in mom_factor.columns[1:]:
        mom_factor[col] = pd.to_numeric(mom_factor[col]) / 100

    # Rename momentum factor to eliminate white space
    mom_factor.rename(columns={mom_factor.columns[1] : 'MOM'}, inplace=True)

    return mom_factor


def carhart4Factor(frequency='d'):
    '''
    Returns Fama French 3 factors (Market Risk Premium, SMB, HML), and Momentum

    Set frequency as:
        'd' for daily factors
        'm' for monthly factors
        'a' for annual factors
    '''
    if frequency == 'd':
        ff3_factors = famaFrench3Factor(frequency='d')
        mom_factor = momentumFactor(frequency='d')

    elif frequency == 'm':
        ff3_factors = famaFrench3Factor(frequency='m')
        mom_factor = momentumFactor(frequency='m')

    elif frequency == 'a':
        ff3_factors = famaFrench3Factor(frequency='a')
        mom_factor = momentumFactor(frequency='a')

    carhart_4_factor = pd.merge(ff3_factors, mom_factor,
                                    on='Date', how='left')
    return carhart_4_factor


def famaFrench5Factor(frequency='d'):
    '''
    Returns Fama French 5 factors (Market Risk Premium, SMB, HML, RMW, CMA),
    and the risk-free rate (RF)
    '''
    rows_to_skip = 3

    if frequency == 'd':
        ff5_raw_data = ff_factor_dict['csv_links'][4]
        ff5_factors = pd.read_csv(ff5_raw_data, skiprows=rows_to_skip)
        ff5_factors.rename(columns={ff5_factors.columns[0]: 'Date'},
                           inplace=True)
        # Ignore copyright footer     
        ff5_factors = ff5_factors.iloc[:-2]
        ff5_factors['Date'] = pd.to_datetime(ff5_factors['Date'],
                                                    format='%Y%m%d')
    else:
        ff5_raw_data = ff_factor_dict['csv_links'][3]
        ff5_factors = pd.read_csv(ff5_raw_data, skiprows=rows_to_skip)
        ff5_factors.rename(columns = {ff5_factors.columns[0] : 'Date'},
                           inplace=True)

        # Get index of annual factor returns
        annual_factor_index_loc = ff5_factors[
                ff5_factors.values == ' Annual Factors: January-December '].index

        # Clean annual and monthly versions
        if frequency == 'm':
            ff5_factors.drop(ff5_factors.index[annual_factor_index_loc[0]:], inplace=True)

            # Convert dates to pd datetime objects
            ff5_factors['Date'] = pd.to_datetime(ff5_factors['Date'],
                                                            format='%Y%m')
            # Shift dates to end of month
            ff5_factors['Date'] = ff5_factors['Date'].apply(
                lambda date : date + relativedelta(day = 1, months = +1, days = -1))

        elif frequency == 'a':
            # Extract annual data only
            ff5_factors.drop(ff5_factors.index[:annual_factor_index_loc[0]],
                             inplace=True)

            # Ignore copyright footer & first 2 header rows
            ff5_factors = ff5_factors.iloc[2:]
            ff5_factors.reset_index(inplace=True)
            ff5_factors.drop(columns=ff5_factors.columns[0], inplace=True)

            # Deal with spacing issues (e.g. '  1927' instead of '1927')
            ff5_factors['Date'] = ff5_factors['Date'].apply(
                lambda x : x.strip())

            # Convert dates to datetime objects (note: values will be int64)
            ff5_factors['Date'] = pd.to_datetime(ff5_factors['Date']+"1231",
                                                            format='%Y%m%d')

    # Convert all factors to numeric and decimals (%)
    for col in ff5_factors.columns[1:]:
        ff5_factors[col] = pd.to_numeric(ff5_factors[col]) / 100

    return ff5_factors
