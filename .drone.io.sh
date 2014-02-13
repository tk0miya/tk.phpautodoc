#!/bin/sh
sudo apt-get install python2.6 python2.6-dev

pip install detox --use-mirrors
detox
