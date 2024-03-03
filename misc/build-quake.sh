#!/bin/bash -i
# 1
cdt1
gamedir="/mnt/mss/stuff/media/games/ioquake3"

gcd1 https://github.com/ioquake/ioq3.git
cd   ioq3/

mymake(){
 make \
  BUILD_STANDALONE=0            \
  BUILD_CLIENT=1                \
  BUILD_SERVER=1                \
  BUILD_GAME_SO=0               \
  BUILD_GAME_QVM=0              \
  BUILD_BASEGAME=1              \
  BUILD_MISSIONPACK=1           \
  BUILD_RENDERER_OPENGL2=1      \
  BUILD_AUTOUPDATER=0           \
  CLIENTBIN=q3a                 \
  SERVERBIN=q3a.ded             \
  USE_OPENAL=1                  \
  USE_OPENAL_DLOPEN=0           \
  USE_CURL=1                    \
  USE_CURL_DLOPEN=0             \
  USE_CODEC_VORBIS=1            \
  USE_CODEC_OPUS=0              \
  USE_MUMBLE=0                  \
  USE_VOIP=0                    \
  USE_FREETYPE=1                \
  USE_INTERNAL_LIBS=0           \
  USE_RENDERER_DLOPEN=0         \
  DEFAULT_BASEDIR="${gamedir}"  \
  COPYDIR="${PWD}/KEK/ioquake3" \
 ${@}
}

mkdir "${PWD}"/KEK/ioquake3

mymake
mymake copyfiles

mv "${PWD}"/KEK/ioquake3/{q3a_opengl2.x86_64,q3a.x86_64}
cp -r "${PWD}"/KEK/ioquake3 /mnt/mss/stuff/media/games/

cd ../; rm -rf ioq3/

# 2
gcd1 https://github.com/Shpoike/Quakespasm
cd   Quakespasm/Quake

sed -i -e 's/CFLAGS += -O2//' Makefile

make \
 DEBUG=0            \
 DO_USERDIRS=1      \
 USE_SDL2=1         \
 USE_ZLIB=1         \
 USE_CODEC_WAVE=0   \
 USE_CODEC_FLAC=0   \
 USE_CODEC_MP3=0    \
 USE_CODEC_VORBIS=1 \
 USE_CODEC_OPUS=0

mkdir /mnt/mss/stuff/media/games/quakespasm-spiked/
cp quakespasm /mnt/mss/stuff/media/games/quakespasm-spiked/

cd ../../; rm -rf Quakespasm/ KEK/ SDL2-2.26.4.tar.gz
