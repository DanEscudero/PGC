#!/bin/bash

for i in {0..9}
do
 python3 xml2tables.py ids-doutores/ids$i.txt
done