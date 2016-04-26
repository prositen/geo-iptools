# geo-iptools

* Edit `iptools.py` with the path to your own geo datafiles (not included in the repo)
* `pip install -r requirements.pip`  (preferably inside a virtualenv)


## Command line

* Run `iptools.py iplist.txt > output.csv` 
* `iplist.txt` should contain one IP per line
* `output.csv` will be a CSV where each line contains an IP and the country lookup data for each geo provider

## Webserver

* Run `flask-iptools.py [--port 5001] [--debug]`
* Go to localhost:port/ip
* Paste or upload the ip list
* ...
* Profit!
