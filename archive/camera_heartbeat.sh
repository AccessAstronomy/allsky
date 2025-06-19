if [[ $(gphoto2 --auto-detect | grep Canon | wc -l) = 1 ]] ; then 
    CRONITOR=`crudini --get allsky.ini Cronitor Cronitor_Root`
    curl https://cronitor.link/p/945ebc5a62dd4efebd5f485648aad8bf/$CRONITOR-camera?msg="CameraConnected" 
else
    plug=`crudini --get allsky.ini Paths Camera_Plug_MQQT`
    mosquitto_pub -h localhost -t cmnd/$plug/POWER -m off
    sleep 580
    mosquitto_pub -h localhost -t cmnd/$plug/POWER -m on
fi
