#!/bin/bash

curl -X GET localhost:5000/v1/register -H "Content-Type: application/json" -H "Apr: $1"