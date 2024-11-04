# allsky

Install the 64-bit OS to raspberry Pi, add the system settings for the network, enable ssh
**Please use unique user names from now on e.g. LDST_EOSRP or cronitor confilcts can occur**

To install on a clean raspberry pi paste this command (warning does a lot of deleting, installing and setting up and reboots):
First it asks you some setup information, then runs all the way until it reboots.
```
bash <(curl -sL https://github.com/AccessAstronomy/allsky/raw/refs/heads/main/allsky-setup.sh)
```

* You need to update the slack token in goodmorning.py and archivespace.py
* You need to set the latitude and longitude in allsky.ini
* You need to update the ssh key, and tunnel settings, in the archiving computer
