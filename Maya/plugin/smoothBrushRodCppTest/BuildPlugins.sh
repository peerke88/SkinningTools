#!/usr/bin/env bash
# batch file to build all maya plugins at once
BASEDIR=$(dirname "$0")
Echo "$BASEDIR"
function pause(){
    read -p "$*s"
}

array=( 2017 2018 2019 2020 )

[ ! -d "$BASEDIR/build" ] && mkdir -p "$BASEDIR/build"
cd "$BASEDIR/build"
rm -r *


for i in "${array[@]}"
do
	cmake -g "Unix makefiles" -DMAYA_VERSION=$i ../
	cmake --build . --config Release --target install
	rm -r *
done


pause  'all plugins built press [Enter] to exit'
