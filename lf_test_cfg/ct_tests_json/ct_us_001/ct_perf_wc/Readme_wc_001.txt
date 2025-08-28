This Readme_wc_001.txt is to assist in running the lf_check.py test suites on the various test setups 

To run lf_check.py change to lanforge-scripts/py-scripts/tools

The format for the command is 
./lf_check.py --json_rig <rig json> --json_dut <dut json>  --json_tests <test json>:<test suite>,<test json>:<test suite> --path /home/lanforge/html-report/<directory>  --log_level debug

For a production run ad --production to email to a wider audiance 


./lf_check.py --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_001 --log_level debug


########################
TESTBED 001 WC test runs
########################

# 2G
./lf_check.py --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ath10K_9984_W0,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ath9K_W2,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ax200_W4,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ax210_W5,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_001 --log_level debug

#5G
./lf_check.py --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ath10K_9984_W1,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ath9K_W2,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ax200_W4,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ax210_W5,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_001 --log_level debug


#ALL Individually 
./lf_check.py --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ath10K_9984_W1,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ath9K_W2,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ax200_W4,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_ax210_W5,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001.json:wc_perf_5g_mtk7915_W7,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ath10K_9984_W0,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ath9K_W2,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ax200_W4,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_ax210_W5,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001.json:wc_perf_2g_mtk7915_W7  --path /home/lanforge/html-reports/ct_us_001 --log_level debug

####################
# ALL at one time
####################
./lf_check.py --db_override ./tools/CT_001_WC_PERF.db --json_rig ./ct_rig_json/ct_us_001_rig.json --json_dut ./ct_dut_json/ct_001_AX88U_dut.json --json_test ./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_2g_001_W0_W2_W4_W5_W7.json:wc_perf_2g_W0_W2_W4_W5_W7,./ct_tests_json/ct_us_001/ct_perf_wc/ct_perf_wc_5g_001_W1_W2_W4_W5_W7.json:wc_perf_5g_W1_W2_W4_W5_W7 --path /home/lanforge/html-reports/ct_us_001 --log_level debug
