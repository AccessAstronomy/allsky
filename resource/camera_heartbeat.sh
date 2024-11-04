if [[ $(gphoto2 --auto-detect | grep Canon | wc -l) = 1 ]] ; then 
    curl https://cronitor.link/p/945ebc5a62dd4efebd5f485648aad8bf/ldst-eosrp-camera?msg="CameraConnected" 
else
    mosquitto_pub -h localhost -t cmnd/eosrpcam/POWER -m off
    sleep 5
    mosquitto_pub -h localhost -t cmnd/eosrpcam/POWER -m on
fi
