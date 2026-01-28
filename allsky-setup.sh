cd $HOME

echo -n "Enter Location Name (e.g. Zernike) "
read locate
echo -n "Enter Camera Type (e.g. EOSRP or SQC) "
read CAMERA

DEVICE=$locate"_"$CAMERA

SUFFIX="cr3"
PREFIX="RP"

if [ $CAMERA = "SQC" ]
    then 
        SUFFIX="cr2"
        PREFIX="SQC"
fi

declare -l llocate=$locate
declare -l lcamera=$CAMERA

CRONROOT=$llocate"-"$lcamera
PLUG=$lcamera"cam"

PIKEY=UyrkBwe3s8
CRONKEY=b4b19cf1b622490186a8ce795d85d981

rm -r $HOME/*

GITROOT=https://github.com/AccessAstronomy/allsky/raw/refs/heads/main/resource

wget $GITROOT/allsky-default.ini
mv allsky-default.ini allsky.ini
curl https://stem.ooo/skey/slack.txt >> allsky.ini

wget $GITROOT/allsky-latest.py
wget $GITROOT/archivespace.py
wget $GITROOT/auto_start_script.sh
wget $GITROOT/camera_heartbeat.sh
wget $GITROOT/check_space.bash
wget $GITROOT/goodmorning.bash
wget $GITROOT/goodmorning.py
wget $GITROOT/slacker_2.py
wget $GITROOT/slacker_2.bash

sudo apt update
sudo apt upgrade -y
sudo apt install gphoto2 -y
sudo apt install python3-pillow -y
sudo apt install python3-scipy -y
sudo apt install python3-ephem -y
sudo apt install python3-matplotlib -y
sudo apt install python3-astropy -y
sudo apt install crudini -y
sudo apt install mosquitto -y
sudo apt install mosquitto-clients -y
python3 -m venv env
env/bin/pip install slack-sdk slack_sdk

crudini --set allsky.ini Paths Camera_ID $DEVICE
crudini --set allsky.ini Paths Camera_Plug_MQQT $PLUG
crudini --set allsky.ini Paths Home $HOME
crudini --set allsky.ini Camera Prefix $PREFIX
crudini --set allsky.ini Camera Suffix $SUFFIX
crudini --set allsky.ini Cronitor Cronitor_Key $CRONKEY
crudini --set allsky.ini Cronitor Cronitor_Root $CRONROOT

ssh-keygen -f ~/.ssh/id_rsa -N ''
sudo mkdir /home/Archive
sudo chown $USER /home/Archive
mkdir /home/Archive/$DEVICE

curl -s https://pitunnel.com/get/$PIKEY | sudo bash 
pitunnel --port=22 --name=$DEVICE --persist
pitunnel --port=1883 --name=MQQT$DEVICE --persist

curl https://cronitor.io/install-linux?sudo=1 -H "API-KEY: $CRONKEY"  | sh

line="@reboot bash $HOME/auto_start_script.sh"
(crontab -l; echo "$line" ) | crontab -

line="00 16 * * * bash $HOME/auto_start_script.sh"
(crontab -l; echo "$line" ) | crontab -
line="*/59 * * * * bash camera_heartbeat.sh"
(crontab -l; echo "$line" ) | crontab -  
line="30 15 * * * bash check_space.bash"
(crontab -l; echo "$line" ) | crontab -  
line="30 7 * * * bash goodmorning.bash"
(crontab -l; echo "$line" ) | crontab -  

echo 'listener 1883' | sudo tee -a /etc/mosquitto/mosquitto.conf
echo 'allow_anonymous true' | sudo tee -a /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto

source check_space.bash

sudo raspi-config nonint do_boot_behaviour B2
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_vnc 0

sudo reboot

