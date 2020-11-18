#!/bin/bash

for i in 0 1 2 3 5 6 7 8 9
do
 python3 xml2tables.py ids-doutores/ids$i.txt
done