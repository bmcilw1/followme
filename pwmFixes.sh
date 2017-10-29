# See what's going on
for i in `find /sys/devices/platform/ocp/ -type f |grep pinmux |grep state$|sort -n`; do echo $i: `cat $i`; done

# Configure appropiate ports as PWM
config-pin -q p9.14
config-pin p9.14 pwm
config-pin -q p9.14

config-pin -q p9.16
config-pin p9.16 pwm
config-pin -q p9.16

config-pin -q p8.19
config-pin p8.19 pwm
config-pin -q p8.19

config-pin -q p8.13
config-pin p8.13 pwm
config-pin -q p8.13
