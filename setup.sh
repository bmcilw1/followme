#!/bin/bash

# Get pyserial plugin
if [ $1=="p" ]
then
    sudo apt-get install python-serial
fi

# Git config
if [ $1=="b" ]
then
    git config --global user.name "Brian McIlwain"
    git config --global user.email "bmcilw1@gmail.com"
    
    # Get .configs setup
    cd ~
    git clone https://github.com/bmcilw1/configs.git ~ && cp -r ~/configs/. ~/. && rm -rf ~/configs
    curl -fLo ~/.vim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    vim -c PlugInstall
fi
