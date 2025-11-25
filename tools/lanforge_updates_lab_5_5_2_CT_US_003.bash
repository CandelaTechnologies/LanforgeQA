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
echo "Updates to CT-US-003-1 (APU2) 192.168.100.181"; \
./lf_update.py \
--tb_name CT-US-003-1 \
--mgr 192.168.100.181 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 25 \
--root_timeout 1800 \
--log_level info \
> /tmp/CT-US-003-1.log &


echo "Updates to CT-US-003-2 (APU2) 192.168.100.152"; \
./lf_update.py \
--tb_name CT-US-003-2 \
--mgr 192.168.100.152 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 25 \
--root_timeout 1800 \
--log_level info \
> /tmp/CT-US-003-2.log &



echo "Updates to CT-US-003-3 (APU2) 192.168.100.192"; \
./lf_update.py \
--tb_name CT-US-003-3 \
--mgr 192.168.100.192 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 25 \
--root_timeout 1800 \
--log_level info \
> /tmp/CT-US-003-3.log &


echo "Updates to CT-US-003-4 (Noah2) 192.168.102.52"; \
./lf_update.py \
--tb_name CT-US-003-4 \
--mgr 192.168.102.52 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 20 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-003-4.log &


echo "Updates to CT-US-003-5 (Noah2) 192.168.102.133"; \
./lf_update.py \
--tb_name CT-US-003-5 \
--mgr 192.168.102.133 \
--root_user root \
--root_password lanforge \
--user lanforge \
--user_password lanforge \
--mgr_ssh_port 22 \
--lfver 5.5.2 \
--kver 6.15.6+ \
--user_timeout 20 \
--root_timeout 720 \
--log_level info \
> /tmp/CT-US-003-5.log &


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





