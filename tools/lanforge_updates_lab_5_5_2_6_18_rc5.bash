#!/bin/bash

# Function to display the spinner for a given PID
spin() {
    local pid="$1"
    local delay=0.1
    local spinchars="/-\\|"
    local i=0

    while kill -0 "$pid" 2>/dev/null; do
        local char=${spinchars:i++ % ${#spinchars}:1}
        echo -ne "\r$char"
        sleep $delay
    done
}

# Start your background commands
# Start your background commands
echo "Updates to CT-ID-103"; \
./lf_update.py \
--tb_name CT-ID-103 \
--mgr 192.168.50.103 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-ID-103.log &

echo "Updates to CT-US-001 192.168.100.116"; \
./lf_update.py \
--tb_name CT-US-001 \
--mgr 192.168.100.116 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-001.log &


echo "Updates to CT-US-002 - 192.168.101.18"; \
./lf_update.py \
--tb_name CT-US-002 \
--mgr 192.168.101.18 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-002.log &



echo "Updates to CT-US-004 - 192.168.100.194"; \
./lf_update.py \
--tb_name CT-US-004 \
--mgr 192.168.100.194 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-004.log &


echo "Updates to CT-US-005-1 192.168.100.132"; \
./lf_update.py \
--tb_name CT-US-005-1 \
--mgr 192.168.100.132 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-005-1.log &


echo "Updates to CT-US-005-2 - 192.168.101.91"; \
./lf_update.py \
--tb_name CT-US-005-2 \
--mgr 192.168.101.91 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-005-2.log &


echo "Updates to CT-US-007 - 192.168.102.197"; \
./lf_update.py \
--tb_name CT-US-007 \
--mgr 192.168.102.197 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-007.log &


echo "Updates to CT-US-008-1 192.168.101.137"; \
./lf_update.py \
--tb_name CT-US-008-1 \
--mgr 192.168.101.137 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-008-1.log &


echo "Updates to CT-US-008-2 192.168.101.117"; \
./lf_update.py \
--tb_name CT-US-008-2 \
--mgr 192.168.101.117 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-008-2.log &


echo "Updates to CT-US-008-3 192.168.102.212"; \
./lf_update.py \
--tb_name CT-US-008-3 \
--mgr 192.168.102.212 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-008-2.log &


echo "Updates to CT-US-009 192.168.100.221"; \
./lf_update.py \
--tb_name CT-US-009 \
--mgr 192.168.100.221 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.18.0-rc5+ \
--user_timeout 10 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-009.log &

# Get the PIDs of the background jobs
pids=($!)

# Start the spinner for each PID in the background
for pid in "${pids[@]}"; do
    spin "$pid" &
    spinners+=($!)  # Capture the spinner PID
done

# Wait for all background processes to finish
wait "${pids[@]}"

# Clear the spinner line after all processes complete
for spinner in "${spinners[@]}"; do
    kill "$spinner" 2>/dev/null
done

echo -ne "\rCompleted.\n"





