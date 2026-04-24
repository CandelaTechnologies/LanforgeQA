#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "CT_US_005 Running ct_us_005_qa_suite"

echo "CT_US_005 Running ap_auto"
./ct_us_005_ap_auto.bash
