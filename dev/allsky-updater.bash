#!/bin/bash

version=$(grep -Eo "__version__\s*=\s*['\"][^'\"]+['\"]" allsky-latest.py | sed -E "s/.*['\"]([^'\"]+)['\"].*/\1/")

if [ -z "$version" ]; then
    echo "Could not determine version from allsky-latest.py"
    exit 1
fi

if [ $version = "9.2.j.log" ]
    then 
        echo "Updating to version 9.3.j.log"
        wget https://github.com/your/repo/archive/refs/tags/v9.3.j.log.py -O allsky-latest.py
        version="9.3.j.log"
fi

if [ $version = "9.3.j.log" ]
    then 
        echo "Already at version 9.3.j.log"
        exit 0
fi
