#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Dataplane Tests"
./lf_check.py \
--db_override ./tools/CT_002_DP_PERF_START_JAN_2024.db \
--json_rig ./ct_rig_json/ct_us_002_rig.json \
--json_dut ./ct_dut_json/ct_002_AX16K_dut.json \
--json_test \
./ct_tests_json/ct_us_002/ct_perf_dp/ct_perf_dp_2g_002_W0_W2_W3_W4_W5_W6_W7_rx.json:dp_perf_2g_W0_W2_W3_W4_W5_W6_W7_rx,\
./ct_tests_json/ct_us_002/ct_perf_dp/ct_perf_dp_2g_002_W0_W2_W3_W4_W5_W6_W7_tx.json:dp_perf_2g_W0_W2_W3_W4_W5_W6_W7_tx,\
./ct_tests_json/ct_us_002/ct_perf_dp/ct_perf_dp_5g_002_W1_W2_W3_W4_W5_W6_W7_rx.json:dp_perf_5g_W1_W2_W3_W4_W5_W6_W7_rx,\
./ct_tests_json/ct_us_002/ct_perf_dp/ct_perf_dp_5g_002_W1_W2_W3_W4_W5_W6_W7_tx.json:dp_perf_5g_W1_W2_W3_W4_W5_W6_W7_tx,\
./ct_tests_json/ct_us_002/ct_perf_dp/ct_perf_dp_6g_002_W5_W6_rx.json:dp_perf_6g_W5_W6_rx,\
./ct_tests_json/ct_us_002/ct_perf_dp/ct_perf_dp_6g_002_W5_W6_tx.json:dp_perf_6g_W5_W6_tx \
--path /home/lanforge/html-reports/ct_us_002 \
--log_level debug \
--production
