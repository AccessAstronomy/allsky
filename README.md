# allsky

Install the 64-bit OS to raspberry Pi, add the system settings for the network, enable ssh
**Please use unique user names from now on e.g. LDST_EOSRP or cronitor confilcts can occur**

To install on a clean raspberry pi paste this command (warning does a lot of deleting, installing and setting up and reboots):
First it asks you some setup information, then runs all the way until it reboots.
```
bash <(curl -sL https://github.com/AccessAstronomy/allsky/raw/refs/heads/main/allsky-setup.sh)
```
* You may need to run the below to fix the installed files (until implemented) if %>bash auto_start_script.sh gives you errors like '\r':
```
bash <(curl -sL https://github.com/AccessAstronomy/allsky/raw/refs/heads/main/patch.sh)
```

* To install the environment sensor monitoring run:
```
bash <(curl -sL https://github.com/AccessAstronomy/allsky/raw/refs/heads/main/enviro_installer.sh)
```

* To patch the wormgat tunnel-by-apsys run:
```
bash <(curl -sL https://raw.githubusercontent.com/AccessAstronomy/wormgat/refs/heads/main/auto_tunnel.sh)
```

* To remove pi-tunnel, FIRST! log in via wormgat, then run:
curl -sL https://pitunnel.com/uninstall | sudo python

* There is generally a large linux install tarball in the home directory that you can delete
* You need to update the slack token in allsky.ini if not there
* You need to set the latitude and longitude in allsky.ini
* You need to update the ssh key, and tunnel settings, in the archiving computer
```
ssh-copy-id sqc@uk1.pitunnel.com -p 22184
```
