# getFamaFrenchFactors.py
# Author: Vash
# Version 1.4
# Last updated: 18 May 2019

"""
This programme gets cleaned versions of factors including:
    * Fama French 3 factor (MRP, SMB, HML)
    * Momentum (MOM)
    * Carhart 4 factors (MRP, SMB, HML, MOM)
    * Fama French 5 factors (MRP, SMB, HML, RMW, CMA)

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
all_factors_text = soup.findAll('b', text=text_to_search)

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

ff3factor_dict = dict(all_factor_links[0])
momAndOthers_dict = dict(all_factor_links[1])


def famaFrench3Factor(frequency='m'):
    '''
    Returns Fama French 3 factors (Market Risk Premium, SMB, HML)

    Set frequency as:
        'm' for monthly factors
        'a' for annual factors

    '''
    rows_to_skip = 3
    ff3_raw_data = ff3factor_dict['csv_links'][0]

    ff3_factors = pd.read_csv(ff3_raw_data, skiprows=rows_to_skip)
    ff3_factors.rename(columns = {ff3_factors.columns[0] : 'date_ff_factors'},
                       inplace=True)

    # Get index of annual factor returns
    annual_factor_index_loc = ff3_factors[
            ff3_factors.values == ' Annual Factors: January-December '].index

    # Clean annual and monthly versions
    if frequency == 'm':
        ff3_factors.drop(ff3_factors.index[annual_factor_index_loc[0]:], inplace=True)

        # Convert dates to pd datetime objects
        ff3_factors['date_ff_factors'] = pd.to_datetime(ff3_factors['date_ff_factors'],
                                                        format='%Y%m')
        # Shift dates to end of month
        ff3_factors['date_ff_factors'] = ff3_factors['date_ff_factors'].apply(
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
        ff3_factors['date_ff_factors'] = ff3_factors['date_ff_factors'].apply(
            lambda x : x.strip())

        # Convert dates to datetime objects (note: values will be int64)
        ff3_factors['date_ff_factors'] = pd.to_datetime(ff3_factors['date_ff_factors'],
                                                        format='%Y').dt.year.values


    # Convert all factors to numeric and decimals (%)
    for col in ff3_factors.columns[1:]:
        ff3_factors[col] = pd.to_numeric(ff3_factors[col]) / 100

    return ff3_factors


def momentumFactor(frequency='m'):
    '''
    Returns the Momentum factor

    Set frequency as:
        'm' for monthly factors
        'a' for annual factors

    '''
    rows_to_skip = 13
    mom_raw_data = momAndOthers_dict['csv_links'][0]

    mom_factor = pd.read_csv(mom_raw_data, skiprows=rows_to_skip)
    mom_factor.rename(columns = {mom_factor.columns[0] : 'date_ff_factors'},
                      inplace=True)

    # Get index of annual factor returns
    annual_factor_index_loc = mom_factor[
            mom_factor.values == 'Annual Factors:'].index
    # Clean annual and monthly versions
    if frequency == 'm':
        # Exclude annual factor returns
        mom_factor.drop(mom_factor.index[annual_factor_index_loc[0]:], inplace=True)

        # Convert dates to pd datetime objects
        mom_factor['date_ff_factors'] = pd.to_datetime(mom_factor['date_ff_factors'],
                                                       format='%Y%m')

        # Shift dates to end of month
        mom_factor['date_ff_factors'] = mom_factor['date_ff_factors'].apply(
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
        mom_factor['date_ff_factors'] = mom_factor['date_ff_factors'].apply(
            lambda x : x.strip())

        # Convert dates to datetime objects (note: values will be int64)
        mom_factor['date_ff_factors'] = pd.to_datetime(mom_factor['date_ff_factors'],
                                                       format='%Y').dt.year.values

    # Convert all factors to numeric and decimals (%)
    for col in mom_factor.columns[1:]:
        mom_factor[col] = pd.to_numeric(mom_factor[col]) / 100

    # Rename momentum factor to eliminate white space
    mom_factor.rename(columns={mom_factor.columns[1] : 'MOM'}, inplace=True)

    return mom_factor



def carhart4Factor(frequency='m'):
    '''
    Returns Fama French 3 factors (Market Risk Premium, SMB, HML), and Momentum

    Set frequency as:
        'm' for monthly factors
        'a' for annual factors
    '''

    if frequency == 'm':
        ff3_factors = famaFrench3Factor(frequency='m')
        mom_factor = momentumFactor(frequency='m')

        carhart_4_factor = pd.merge(ff3_factors, mom_factor,
                                    on='date_ff_factors', how='left')
    elif frequency == 'a':
        ff3_factors = famaFrench3Factor(frequency='a')
        mom_factor = momentumFactor(frequency='a')

        carhart_4_factor = pd.merge(ff3_factors, mom_factor,
                                    on='date_ff_factors', how='left')

    return carhart_4_factor


def famaFrench5Factor(frequency='m'):
    '''
    Returns Fama French 5 factors (Market Risk Premium, SMB, HML, RMW, CMA),
    and the risk-free rate (RF)
    '''
    rows_to_skip = 3
    ff5_raw_data = ff3factor_dict['csv_links'][3]

    ff5_factors = pd.read_csv(ff5_raw_data, skiprows=rows_to_skip)
    ff5_factors.rename(columns = {ff5_factors.columns[0] : 'date_ff_factors'},
                       inplace=True)

    # Get index of annual factor returns
    annual_factor_index_loc = ff5_factors[
            ff5_factors.values == ' Annual Factors: January-December '].index

    # Clean annual and monthly versions
    if frequency == 'm':
        ff5_factors.drop(ff5_factors.index[annual_factor_index_loc[0]:], inplace=True)

        # Convert dates to pd datetime objects
        ff5_factors['date_ff_factors'] = pd.to_datetime(ff5_factors['date_ff_factors'],
                                                        format='%Y%m')
        # Shift dates to end of month
        ff5_factors['date_ff_factors'] = ff5_factors['date_ff_factors'].apply(
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
        ff5_factors['date_ff_factors'] = ff5_factors['date_ff_factors'].apply(
            lambda x : x.strip())

        # Convert dates to datetime objects (note: values will be int64)
        ff5_factors['date_ff_factors'] = pd.to_datetime(ff5_factors['date_ff_factors'],
                                                        format='%Y').dt.year.values

    # Convert all factors to numeric and decimals (%)
    for col in ff5_factors.columns[1:]:
        ff5_factors[col] = pd.to_numeric(ff5_factors[col]) / 100

    return ff5_factors
