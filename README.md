# TractiveTracker

## Important first note
I am not a python programmer, i wanted to try this in python to increase my experience and to test myself.\
So when you look at this code, do not judge me harshly :D but i'm always open for feedback.

## Purpose
This python script is made to collect Tractive tracker battery levels and put those in a prometheus scrapable state.\
The data that comes out of this script will make it available for me through prometheus and get alerts when the battery for my dogs trackers get too low.


## Usage
```
export TRACTIVE_USER="user@email.tld"
export TRACTIVE_PASS="password"

python3 tractive.py
```