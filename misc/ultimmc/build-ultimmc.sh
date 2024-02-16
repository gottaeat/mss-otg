# 1
cdt1

gcd1 https://github.com/UltimMC/Launcher
cd Launcher/

repodir="/mss/repo"
gamesdir="/mnt/mss/stuff/media/games"

# 2
pdir="${repodir}/misc/ultimmc/patches/"
for i in "${pdir}"/*.patch; do patch -p1 < "${i}"; done

mkdir build/
cd    build/

cmake -Wno-dev -GNinja \
 -DCMAKE_INSTALL_PREFIX="${gamesdir}/ultimmc"   \
 -DCMAKE_C_FLAGS="$CFLAGS"                      \
 -DCMAKE_CXX_FLAGS="$CXXFLAGS"                  \
 -DCMAKE_EXE_LINKER_FLAGS="$LDFLAGS"            \
 -DCMAKE_SHARED_LINKER_FLAGS="$LDFLAGS"         \
\
 ../

samu
samu install

find "${gamesdir}/ultimmc" -type f -exec strip --strip-all {} ';'

cd ../../; rm -rf Launcher/
