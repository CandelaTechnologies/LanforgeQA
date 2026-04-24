#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "CT_US_008 Running ct_us_008_qa_suite"

echo "Running functional tests ct_us_008_func_run.bash"
./ct_us_008_func_run.bash

echo "Running data plane ct_us_008_dp_BE19000.bash"
./ct_us_008_dp_BE19000.bash

echo "Running RvR ct_us_008_rvr_BE19000.bash"
./ct_us_008_rvr_BE19000.bash

echo "Running VAP RvR tests (not being run)"
./ct_us_008_rvr_VAP_AT7.bash
