from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(name='getFamaFrenchFactors',
      version='0.0.5',
      description='Returns Fama French Factors as a Pandas Dataframe',
      long_description = long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.7',
      ],
      url='https://vash.uk/python-for-finance/',
      author='Vashisht Bhatt',
      author_email='info@vash.uk',
      license='MIT',
      py_modules=['getFamaFrenchFactors'],
      package_dir={'': 'src'},
      install_requires=[
          'pandas',
          'requests',
          'bs4'
      ],
      include_package_data=True,
      zip_safe=False)
