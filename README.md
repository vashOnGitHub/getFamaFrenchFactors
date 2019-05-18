# getFamaFrenchFactors

This programme gets data for fame french factors from the Kenneth French library and returns it as a pandas dataframe.

## Installation

Run the following to install:

```python
pip install getFamaFrenchFactors
```

## Usage
Factors can be extracted in monthly ('m') and annual ('a') frequencies. The default is monthly.

```python
import getFamaFrenchFactors as gff

# Get the Fama French 3 factor model (monthly data)
df_ff3_monthly = gff.famaFrench3Factor(frequency='m') 

# Get the Fama French 3 factor model (annual data)
df_ff3_annual = gff.famaFrench3Factor(frequency='a')
```

Other options:

* Momentum factor: momentumFactor()
* Carhart 4 factor: carhart4Factor()
* Fama French 5 factor: famaFrench5Factor()
