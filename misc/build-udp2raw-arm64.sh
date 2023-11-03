# 1
cdt1

tar xf /mss/work/sauces/toolchains/aarch64-linux-musl-cross.tgz

tc="/mss/work/table/aarch64-linux-musl-cross/bin/aarch64-linux-musl-"
export        CC="${tc}gcc"
export       CXX="${tc}g++"
export        LD="${tc}ld"
export        AR="${tc}gcc-ar"
export        AS="${tc}as"
export        NM="${tc}gcc-nm"
export     STRIP="${tc}strip"
export    RANLIB="${tc}gcc-ranlib"
export   OBJCOPY="${tc}objcopy"
export   OBJDUMP="${tc}objdump"
export   OBJSIZE="${tc}size"
export   READELF="${tc}readelf"
export ADDR2LINE="${tc}addr2line"

# 2
a2 https://github.com/wangyu-/udp2raw/archive/refs/tags/20230206.0.tar.gz
tar xf 20230206.0.tar.gz
cd     udp2raw-20230206.0/

export   CFLAGS="$(echo "${CFLAGS}" | sed 's/-march=x86-64 -mtune=generic//')"
export CXXFLAGS="$(echo "${CXXFLAGS}" | sed 's/-march=x86-64 -mtune=generic//')"
export  LDFLAGS="$(echo "${LDFLAGS}" | sed 's/-march=x86-64 -mtune=generic//')"

make OPT="$CXXFLAGS $LDFLAGS -static" fast cc_local=$CXX
$STRIP --strip-all udp2raw
