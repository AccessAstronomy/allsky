cd $HOME

wget https://raw.githubusercontent.com/AccessAstronomy/allsky/main/resource/allsky-enviromon/enviromon.py
wget https://raw.githubusercontent.com/AccessAstronomy/allsky/main/resource/allsky-enviromon/enviromon.bash

env/bin/pip install numpy
env/bin/pip install openmeteo_requests
env/bin/pip install requests_cache
env/bin/pip install retry_requests
env/bin/pip install adafruit-circuitpython-dht

sudo apt-get install exiftool -y

chmod +x enviromon.bash

line="*/5 * * * * bash enviromon.bash"
(crontab -l; echo "$line" ) | crontab -
