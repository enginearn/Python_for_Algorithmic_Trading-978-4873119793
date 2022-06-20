#!bin/bash/

sudo apt-get update && sudo apt-get upgrade -y
sudo apt-install -y bzip2 gcc git htop screen vim wget
sudo apt-get upgrade -y bash
sudo apt-get clean

wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O \
        Miniconda.sh
bash Miniconda.sh -b
rm -rf Miniconda.sh
export PATH="$HOME/miniconda3/bin:$PATH"

conda install -y pandas jupyterlab

cd $HOME
# wget https://home.tpq.io/hilpisch/.vimrc