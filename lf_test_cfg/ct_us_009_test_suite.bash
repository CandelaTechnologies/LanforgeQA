#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Functional tests against ASUS BE96U"
./ct_us_009_func_ASUS_BE96U.bash

echo "Running Dataplane against BE800"
./ct_us_009_dp_BE800.bash

echo "Running Wifi Capacity Tests"
./ct_us_009_wc_BE800.bash

echo "Running RvR BE800"
./ct_us_009_rvr_BE800.bash
