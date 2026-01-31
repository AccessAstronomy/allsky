#!/user/bin/env bash
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
USER=${USER:-$(id -un)}
HOME=${HOME:-/home/$USER}

source $HOME/env/bin/activate
VERSION="0.1.2"

if [ ! -f "$HOME/enviro.dat" ]; then
    echo "# # -*- coding: utf-8 -*-" > "$HOME/enviro.dat"
    echo "Header_Rows = 13, 14" >> "$HOME/enviro.dat"
    echo "Data_Rows_Start = 16" >> "$HOME/enviro.dat"
    echo "N_Cols = 12" >> "$HOME/enviro.dat"
    echo "Device =" "$USER" >> "$HOME/enviro.dat"
    echo "Latitude =" "$(grep Camera_Latitude $HOME/allsky.ini | cut -d '=' -f2 | tr -d ' ')" >> "$HOME/enviro.dat"
    echo "Longitude =" "$(grep Camera_Longitude $HOME/allsky.ini | cut -d '=' -f2 | tr -d ' ')" >> "$HOME/enviro.dat"
    version=$(grep -Eo "__version__\s*=\s*['\"][^'\"]+['\"]" "$HOME/enviromon.py" | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/")
    echo "enviromon.py_version = $version" >> "$HOME/enviro.dat"
    echo "file_script_version = enviromon.bash $VERSION #VALUE SHOULD MATCH ABOVE" >> "$HOME/enviro.dat"
    allsky_version=$(grep -Eo "__version__\s*=\s*['\"][^'\"]+['\"]" "$HOME/allsky-latest.py" | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/")
    echo "allsky.py_version = $allsky_version" >> "$HOME/enviro.dat"
    echo "Create_Date =" "$(date +"%Y-%m-%d_%H:%M:%S")" >> "$HOME/enviro.dat"
    echo "----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----" >> "$HOME/enviro.dat"
    echo "Date Time Box_Temp Box_Humidity CPU_Temp EXIF_CCD_Temp EXIF_Color_Temp Current_Temperature_2m Current_Relative_Humidity_2m Current_Cloud_Cover Current_Precipitation Current_Visibility" >> "$HOME/enviro.dat"
    echo "(UTC) (UTC) (°C) (%) (°C) (°C) (K) (°C) (%) (%) (mm/15min) (m)" >> "$HOME/enviro.dat"
    echo "----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----" >> "$HOME/enviro.dat"
fi

python enviromon.py
tail -n 1 "$HOME/enviro.dat" > "$HOME/enviro.out"