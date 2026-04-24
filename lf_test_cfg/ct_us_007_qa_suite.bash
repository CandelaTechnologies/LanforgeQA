#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "CT_US_007 Running ct_us_007_qa_suite"

echo "CT_US_007 running Data Plane Tests"
./ct_us_007_dp_run.bash

echo "CT_US_007 running RvR Tests"
./ct_us_007_rvr_run.bash
