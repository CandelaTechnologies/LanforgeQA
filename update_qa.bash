#!/bin/bash

# update the QA json files

cp ~/git/lf_test_cfg/LanforgeQA/*.bash  ~/git/lanforge-scripts/py-scripts/tools
cp -r ~/git/lf_test_cfg/LanforgeQA/ct_dut_json ~/git/lanforge-scripts/py-scripts/tools
cp -r ~/git/lf_test_cfg/LanforgeQA/ct_rig_json ~/git/lanforge-scripts/py-scripts/tools
cp -r ~/git/lf_test_cfg/LanforgeQA/ct_tests_json ~/git/lanforge-scripts/py-scripts/tools

