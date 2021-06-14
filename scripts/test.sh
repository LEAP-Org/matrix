#!/bin/bash

curl -X POST localhost:5000/v1/register -H "Content-Type: application/json" -d "{\"apr\": \"$1\"}"