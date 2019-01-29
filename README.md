# outbrain-python-reporting
Simple reporting script for python outbrain wrapper

### Project description:
Reporting script using a self-modified version of outbrain for python, [https://github.com/kmb5/python-outbrain].
The problem is that the online Outbrain interface only allows daily reports to be downloaded aggregated, and not filtered by campaign. This script gives a nice export filtered per campaign for an easy overview and further analysis.
**You need to install my Outbrain module fork for this script to work!!!**

USAGE: 
- Install [https://github.com/kmb5/python-outbrain]
- Fill out outbrain.yml with your credentials
- Add your marketer ID to outbrain_python_reporting.py 
(Can be found by creating and authorizing an outbrain object and calling .get_marketers() on it.)
- Run the script `$ python3 outbrain_python_reporting.py` and follow the instructions in the terminal
