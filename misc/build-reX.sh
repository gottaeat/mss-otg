#!/bin/bash -i
cdt1 

gcd1 https://git.tcp.direct/mss/re3 -b master
cd re3/

./premake5Linux --with-librw --verbose gmake2
./printHash.sh src/extras/GitSHA1.cpp

make \
    -C build \
    verbose=yes \
    config=release_linux-amd64-librw_gl3_glfw-oal

re3dir="/mss/work/table/out/re3"
mkdir "${re3dir}"

cp -rfv \
    bin/linux-amd64-librw_gl3_glfw-oal/Release/re3 \
    gamefiles/* \
    "${re3dir}"

cd ../; rm -rf re3/

# 2
gcd1 https://git.tcp.direct/mss/re3 -b miami
cd re3/

./premake5Linux --with-librw --verbose gmake2
./printHash.sh src/extras/GitSHA1.cpp

make \
    -C build \
    verbose=yes \
    config=release_linux-amd64-librw_gl3_glfw-oal

revcdir="/mss/work/table/out/reVC"
mkdir "${revcdir}"

cp -rfv \
    bin/linux-amd64-librw_gl3_glfw-oal/Release/reVC \
    gamefiles/* \
    "${revcdir}"

cd ../; rm -rf re3/

# 3
strip --strip-all \
 "${re3dir}"/re3  \
 "${revcdir}"/reVC

gamesdir="/mnt/mss/stuff/media/games"
mkdir -pv "${gamesdir}"/re{VC,3}

cp -r "${re3dir}"/* "${gamesdir}"/re3/
cp -r "${revcdir}"/* "${gamesdir}"/reVC/

rm -rf out/
