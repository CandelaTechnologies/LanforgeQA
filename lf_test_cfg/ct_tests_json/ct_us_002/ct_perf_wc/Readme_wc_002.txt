This Readme_wc_002.txt is to assist in running the lf_check.py test suites on the various test setups 

To run lf_check.py change to lanforge-scripts/py-scripts/tools

The format for the command is 
./lf_check.py --json_rig <rig json> --json_dut <dut json>  --json_tests <test json>:<test suite>,<test json>:<test suite> --path /home/lanforge/html-report/<directory>  --log_level debug

For a production run ad --production to email to a wider audiance 

Single run

./lf_check.py --json_rig ./ct_rig_json/ct_us_002_rig.json --json_dut ./ct_dut_json/ct_002_AX12_dut.json --json_test ./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_002 --log_level debug



########################
TESTBED 002 WC test runs
########################

# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_002_rig.json --json_dut ./ct_dut_json/ct_002_AX12_dut.json --json_test ./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ath10K_9984_W0,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ath9K_W2,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ax200_W4,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ax210_W5,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_002 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_002_rig.json --json_dut ./ct_dut_json/ct_002_AX12_dut.json --json_test ./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ath10K_9984_W1,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ath9K_W2,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ax200_W4,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ax210_W5,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_002 --log_level debug


#ALL
./lf_check.py --json_rig ./ct_rig_json/ct_us_002_rig.json --json_dut ./ct_dut_json/ct_002_AX12_dut.json --json_test ./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ath10K_9984_W1,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ath9K_W2,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ax200_W4,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_ax210_W5,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002.json:wc_perf_5g_mtk7915_W7,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ath10K_9984_W0,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ath9K_W2,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ax200_W4_rx,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_ax210_W5_rx,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002.json:wc_perf_2g_mtk7915_W7_rx  --path /home/lanforge/html-reports/ct_us_002 --log_level debug


####################
# ALL at one time
####################
./lf_check.py --json_rig ./ct_rig_json/ct_us_002_rig.json --json_dut ./ct_dut_json/ct_002_AX12_dut.json --json_test ./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_2g_002_W0_W2_W4_W5_W7.json:wc_perf_2g_W0_W2_W4_W5_W7,./ct_tests_json/ct_us_002/ct_perf_wc/ct_perf_wc_5g_002_W1_W2_W4_W5_W7.json:wc_perf_5g_W1_W2_W4_W5_W7 --path /home/lanforge/html-reports/ct_us_002 --log_level debug
