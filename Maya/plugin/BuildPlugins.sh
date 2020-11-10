#!/usr/bin/env bash
# batch file to build all maya plugins at once
BASEDIR=$(dirname "$0")
echo "$BASEDIR"

cd "$BASEDIR/rigSystem"

python resourcecompiler.py
echo "build resources.h"


function pause(){
   read -p "$*"
}
 
pause 'Press [Enter] key to continue...'

array=( 2017 2018 2019 2020 )

cd "$BASEDIR/build"
rm -r *


for i in "${array[@]}"
do
	cmake -g "Unix makefiles" -DMAYA_VERSION=$i ../
	cmake --build . --config Release --target install
	rm -r *
done


pause  'all plugins built press [Enter] to exit'
