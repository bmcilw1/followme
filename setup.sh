#!/bin/bash

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

# Configure UART1
config-pin -q p9.26
config-pin p9.26 uart # RX
config-pin -q p9.26

config-pin -q p9.24
config-pin p9.24 uart # TX
config-pin -q p9.24

# Configure UART2
config-pin -q p9.22
config-pin p9.22 uart # RX
config-pin -q p9.22

config-pin -q p9.21
config-pin p9.21 uart # TX
config-pin -q p9.21

# Get pyserial plugin
sudo apt-get install python-serial

# Git config
if [ $1="b" ]
    then
    git config --global user.name "Brian McIlwain"
    git config --global user.email "bmcilw1@gmail.com"
    
    # Get .configs setup
    cd ~
    git clone https://github.com/bmcilw1/configs.git ~ && cp -r ~/configs/. ~/. && rm -rf ~/configs
    curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    vim -c PlugInstall
fi