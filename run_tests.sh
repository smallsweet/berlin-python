#!/bin/bash

for testfile in $(ls tests); do
	echo "TEST: $testfile start"
	curl -v localhost:5000/randombot -d "@tests/$testfile"
	echo "TEST: $testfile done"
done
