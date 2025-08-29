#!/bin/bash

# update the QA json files

cp ~/git/LanforgeQA/lf_test_cfg/*.bash  ~/git/lanforge-scripts/py-scripts/tools
cp -r ~/git/LanforgeQA/lf_test_cfg/ct_dut_json ~/git/lanforge-scripts/py-scripts/tools
cp -r ~/git/LanforgeQA/lf_test_cfg/ct_rig_json ~/git/lanforge-scripts/py-scripts/tools
cp -r ~/git/LanforgeQA/lf_test_cfg/ct_tests_json ~/git/lanforge-scripts/py-scripts/tools

