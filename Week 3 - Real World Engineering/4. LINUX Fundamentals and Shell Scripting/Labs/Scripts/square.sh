#!/bin/bash
square() {
    local num=$1
    echo $(( num * num ))
}

result=$(square 5)
echo "The square of 5 is $result"
