#!/usr/bin/env bash
# batch file to build all maya plugins at once
array=( 2017 2018 2019 2020 )

cd "../build"
rm -r *


for i in "${array[@]}"
do
	cmake3 -g "Unix makefiles" -DMAYA_VERSION=$i ../
	cmake3 --build . --config Release --target install
	rm -r *
done


pause  'all plugins built press [Enter] to exit'
