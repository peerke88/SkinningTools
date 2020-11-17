#!/usr/bin/env bash
# batch file to build all maya plugins at once
function pause(){
    read -p "$*s"
}
array=( 2017 2018 2019 2020 )

[ ! -d "../build" ] && mkdir -p "../build"
cd "../build"
rm -r *


for i in "${array[@]}"
do
	cmake3 -g "Unix makefiles" -DMAYA_VERSION=$i ../
	cmake3 --build . --config Release --target install
	rm -r *
done


pause  'all plugins built press [Enter] to exit'