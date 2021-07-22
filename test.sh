#!/usr/bin/env bash
zappa update stage
rm 12307-01-1*
wget 'https://smo83p9akf.execute-api.eu-central-1.amazonaws.com/stage/%D7%AA%D7%99%D7%A7/12307-01-18?bypass=true'
