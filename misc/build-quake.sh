#!/bin/bash -i
# 1
cdt1

money="/mss/work/table/KEK"
export          CFLAGS="${CFLAGS}   -L${money}/lib -I${money}/include -fPIC"
export        CXXFLAGS="${CXXFLAGS} -L${money}/lib -I${money}/include -fPIC"
export            PATH="${PATH}:${money}/bin"
export PKG_CONFIG_PATH="${money}/lib/pkgconfig"
export    LIBRARY_PATH="${money}/lib"

a2 https://github.com/libsdl-org/SDL/releases/download/release-2.26.4/SDL2-2.26.4.tar.gz

tar xf SDL2-2.26.4.tar.gz
cd     SDL2-2.26.4/

mkdir build
cd    build

cmake -Wno-dev -GNinja \
 -DCMAKE_INSTALL_PREFIX="${money}"      \
 -DCMAKE_INSTALL_LIBDIR=lib             \
 -DCMAKE_C_FLAGS="$CFLAGS"              \
 -DCMAKE_CXX_FLAGS="$CXXFLAGS"          \
 -DCMAKE_EXE_LINKER_FLAGS="$LDFLAGS"    \
 -DCMAKE_SHARED_LINKER_FLAGS="$LDFLAGS" \
 -DCMAKE_CXX_COMPILER_TARGET="$CHOST"   \
 -DCMAKE_C_COMPILER_TARGET="$CHOST"     \
 -DCMAKE_BUILD_TYPE="Release"           \
\
 -DSDL_3DNOW=OFF                        \
 -DSDL_ALSA=OFF                         \
 -DSDL_ALTIVEC=OFF                      \
 -DSDL_ARMNEON=OFF                      \
 -DSDL_ARMSIMD=OFF                      \
 -DSDL_ARTS=OFF                         \
 -DSDL_ASAN=OFF                         \
 -DSDL_ASSEMBLY=ON                      \
 -DSDL_ASSERTIONS=disabled              \
 -DSDL_ATOMIC=ON                        \
 -DSDL_AUDIO=ON                         \
 -DSDL_BACKGROUNDING_SIGNAL=OFF         \
 -DSDL_CCACHE=OFF                       \
 -DSDL_CLOCK_GETTIME=ON                 \
 -DSDL_COCOA=OFF                        \
 -DSDL_CPUINFO=ON                       \
 -DSDL_DBUS=OFF                         \
 -DSDL_DIRECTFB=OFF                     \
 -DSDL_DIRECTX=OFF                      \
 -DSDL_DISKAUDIO=OFF                    \
 -DSDL_DUMMYAUDIO=OFF                   \
 -DSDL_DUMMYVIDEO=OFF                   \
 -DSDL_ESD=OFF                          \
 -DSDL_EVENTS=ON                        \
 -DSDL_FILE=ON                          \
 -DSDL_FILESYSTEM=ON                    \
 -DSDL_FOREGROUNDING_SIGNAL=OFF         \
 -DSDL_FUSIONSOUND=OFF                  \
 -DSDL_GCC_ATOMICS=OFF                  \
 -DSDL_HAPTIC=OFF                       \
 -DSDL_HIDAPI=ON                        \
 -DSDL_HIDAPI_JOYSTICK=ON               \
 -DSDL_HIDAPI_LIBUSB=OFF                \
 -DSDL_IBUS=ON                          \
 -DSDL_INSTALL_TESTS=OFF                \
 -DSDL_JACK=OFF                         \
 -DSDL_JOYSTICK=ON                      \
 -DSDL_KMSDRM=ON                        \
 -DSDL_KMSDRM_SHARED=ON                 \
 -DSDL_LIBC=ON                          \
 -DSDL_LIBSAMPLERATE=OFF                \
 -DSDL_LOADSO=ON                        \
 -DSDL_LOCALE=ON                        \
 -DSDL_METAL=OFF                        \
 -DSDL_MISC=ON                          \
 -DSDL_MMX=ON                           \
 -DSDL_NAS=OFF                          \
 -DSDL_OFFSCREEN=ON                     \
 -DSDL_OPENGL=ON                        \
 -DSDL_OPENGLES=ON                      \
 -DSDL_OSS=OFF                          \
 -DSDL_PIPEWIRE=OFF                     \
 -DSDL_POWER=ON                         \
 -DSDL_PTHREADS=ON                      \
 -DSDL_PTHREADS_SEM=ON                  \
 -DSDL_PULSEAUDIO=ON                    \
 -DSDL_PULSEAUDIO_SHARED=ON             \
 -DSDL_RENDER=ON                        \
 -DSDL_RENDER_D3D=OFF                   \
 -DSDL_RENDER_METAL=OFF                 \
 -DSDL_RPATH=OFF                        \
 -DSDL_RPI=OFF                          \
 -DSDL_SENSOR=ON                        \
 -DSDL_SHARED=OFF                       \
 -DSDL_SNDIO=OFF                        \
 -DSDL_SSE2=ON                          \
 -DSDL_SSE3=ON                          \
 -DSDL_SSE=ON                           \
 -DSDL_SSEMATH=ON                       \
 -DSDL_STATIC=ON                        \
 -DSDL_STATIC_PIC=ON                    \
 -DSDL_SYSTEM_ICONV=ON                  \
 -DSDL_TEST=ON                          \
 -DSDL_TESTS=OFF                        \
 -DSDL_THREADS=ON                       \
 -DSDL_TIMERS=ON                        \
 -DSDL_VENDOR_INFO="apathy"             \
 -DSDL_VIDEO=ON                         \
 -DSDL_VIRTUAL_JOYSTICK=OFF             \
 -DSDL_VIVANTE=OFF                      \
 -DSDL_VULKAN=OFF                       \
 -DSDL_WASAPI=OFF                       \
 -DSDL_WAYLAND=OFF                      \
 -DSDL_WAYLAND_LIBDECOR=OFF             \
 -DSDL_WAYLAND_LIBDECOR_SHARED=OFF      \
 -DSDL_WAYLAND_QT_TOUCH=OFF             \
 -DSDL_WAYLAND_SHARED=OFF               \
 -DSDL_WERROR=OFF                       \
 -DSDL_X11=ON                           \
 -DSDL_X11_SHARED=ON                    \
 -DSDL_X11_XCURSOR=ON                   \
 -DSDL_X11_XDBE=OFF                     \
 -DSDL_X11_XFIXES=ON                    \
 -DSDL_X11_XINPUT=ON                    \
 -DSDL_X11_XRANDR=ON                    \
 -DSDL_X11_XSCRNSAVER=OFF               \
 -DSDL_X11_XSHAPE=OFF                   \
 -DSDL_XINPUT=ON                        \
 ..

samu
samu install

cd ../../; rm -rf SDL2-2.26.4/

cd "${money}"
rm -rf share/

ars="$(find . -type f -name \*.a)"
for i in ${ars}; do
 strip  --strip-debug "${i}"
 ranlib               "${i}"
done

cd ../

# 2
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
  BUILD_RENDERER_OPENGL2=0      \
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

cp -r "${PWD}"/KEK/ioquake3 /mnt/mss/stuff/media/games/

cd ../; rm -rf ioq3/

# 3
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
 USE_CODEC_OPUS=0   \
 SDL_CONFIG="${money}"/bin/sdl2-config

mkdir /mnt/mss/stuff/media/games/quakespasm-spiked/
cp quakespasm /mnt/mss/stuff/media/games/quakespasm-spiked/

cd ../../; rm -rf Quakespasm/ KEK/ SDL2-2.26.4.tar.gz
