cd $HOME

echo -n "Enter Location Name (e.g. Zernike) "
read locate
echo -n "Enter Camera Type (e.g. SQC) "
read CAMERA
echo -n "Enter File Prefix (e.g. RP or SQC) "
read PREFIX
echo -n "Enter File Suffix (e.g. cr3 or cr2) "
read SUFFIX
DEVICE=$locate"_"$CAMERA

echo -n "Enter Cronitor Root Name (e.g. zernike-sqc) "
read CRONROOT
echo -n "Enter plug topic (e.g. sqccam) "
read PLUG

PIKEY=UyrkBwe3s8
CRONKEY=b4b19cf1b622490186a8ce795d85d981

GITROOT=https://github.com/AccessAstronomy/allsky/raw/refs/heads/main/resource
wget $GITROOT/allsky.ini
wget $GITROOT/allsky-latest.py
wget $GITROOT/archivespace.py
wget $GITROOT/auto_start_script.sh
wget $GITROOT/camera_heartbeat.sh
wget $GITROOT/check_space.bash
wget $GITROOT/goodmorning.bash
wget $GITROOT/goodmorning.py

sudo apt update
sudo apt upgrade -y
sudo apt install gphoto -y
sudo apt install python3-pillow -y
sudo apt install python3-scipy -y
sudo apt install python3-ephem -y
sudo apt install python3-matplotlib -y
sudo apt install python3-astropy -y
sudo apt install crudini -y

crudini --set allsky.ini Paths Camera_ID $DEVICE
crudini --set allsky.ini Paths Camera_Plug_MQQT $PLUG
crudini --set allsky.ini Paths Home $HOME
crudini --set allsky.ini Camera Prefix $PREFIX
crudini --set allsky.ini Camera Suffix $SUFFIX
crudini --set allsky.ini Cronitor Cronitor_Key $CRONKEY
crudini --set allsky.ini Cronitor Cronitor_Root $CRONROOT

curl -s https://pitunnel.com/get/$PIKEY | sudo bash 
pitunnel --port=22 --name=$DEVICE --persist

curl https://cronitor.io/install-linux?sudo=1 -H "API-KEY: $CRONKEY"  | sh

line = "*/10 * * * * bash $HOME/auto_start_script.sh"
(crontab -l; echo "$line" ) | crontab -
cronitor discover --auto

sudo mkdir /home/Archive
sudo chown $USER /home/Archive
mkdir /home/Archive/$DEVICE

python3 -m venv env
env/bin/pip install slack-sdk slack_sdk

line="*/10 * * * * bash camera_heartbeat.sh"
(crontab -l; echo "$line" ) | crontab -  
line="30 15 * * * bash check_space.bash"
(crontab -l; echo "$line" ) | crontab -  
line="30 7 * * * bash goodmorning.bash"
(crontab -l; echo "$line" ) | crontab -  

pitunnel --port=1883 --name=MQQT$DEVICE --persist

sudo apt-get install mosquitto -y
sudo apt-get install mosquitto-clients -y

echo 'listener 1883' | sudo tee -a /etc/mosquitto/mosquitto.conf
echo 'allow_anonymous true' | sudo tee -a /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto

source check_space.bash

sudo raspi-config nonint do_boot_behaviour B2
sudo raspi-config nonint do_ssh 1
sudo raspi-config nonint do_vnc 1

sudo reboot

