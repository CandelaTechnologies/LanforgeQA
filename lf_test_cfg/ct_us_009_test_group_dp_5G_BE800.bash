#!/bin/bash

# allow commands to be printed to the terminal
set -x

echo "Running Wifi Capacity tests"
./lf_check.py \
--db_override ./tools/CT_US_009_TEST_GROUP_DP_PERF_BE800.db \
--json_rig ./ct_rig_json/ct_us_009_TP_LINK_BE800_rig.json \
--json_dut ./ct_dut_json/ct_009_TP_LINK_BE800_dut.json \
--json_test \
./ct_tests_json/ct_us_009/ct_perf_dp_testgroup/TP_LINK_BE800/ct_perf_dp_5G_TP_LINK_test_group_W8_TCP_rx.json:ct_perf_dp_5G_test_group_TCP_rx,\
./ct_tests_json/ct_us_009/ct_perf_dp_testgroup/TP_LINK_BE800/ct_perf_dp_5G_TP_LINK_test_group_W8_TCP_tx.json:ct_perf_dp_5G_test_group_TCP_tx,\
./ct_tests_json/ct_us_009/ct_perf_dp_testgroup/TP_LINK_BE800/ct_perf_dp_5G_TP_LINK_test_group_W8_UDP_rx.json:ct_perf_dp_5G_test_group_UDP_rx,\
./ct_tests_json/ct_us_009/ct_perf_dp_testgroup/TP_LINK_BE800/ct_perf_dp_5G_TP_LINK_test_group_W8_UDP_tx.json:ct_perf_dp_5G_test_group_UDP_tx \
--path /home/lanforge/html-reports/ct_us_009 \
--log_level debug
