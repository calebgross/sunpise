#!/bin/bash

# Usage:
# ./tunnel.sh [start|stop] <SSH_USER> <SSH_HOST>
#
# On remote host, if necessary, consider appending to /etc/sudoers:
# <SSH_USER> ALL = NOPASSWD: /usr/bin/firewall-cmd --add-port=[0-9][0-9][0-9][0-9][0-9]/tcp
#
# /etc/ssh/sshd_config
# GatewayPorts yes

CMD="$1"
USER="$2"
HOST="$3"
LOCAL_SSH="$4"
REMOTE_SSH="$5"
KEY="$6"

open_tunnel() { /usr/bin/ssh -f -i "$KEY" -p "$REMOTE_SSH" "$USER@$HOST" -R "0.0.0.0:$1:127.0.0.1:$LOCAL_SSH" "/usr/bin/sudo /usr/bin/firewall-cmd --add-port=$1/tcp; /usr/bin/sleep infinity" >/dev/null 2>&1; }
tunnel_exists() { /usr/bin/pgrep -f "ssh.*$USER@$HOST.*0.0.0.0:[0-9]{5}:127.0.0.1:$LOCAL_SSH" >/dev/null 2>&1; }
port_bound() { /bin/nc -vz "$HOST" "$1" >/dev/null 2>&1; }

if [ "$CMD" == 'start' ]
then
    if tunnel_exists
    then
        /bin/echo 'Tunnel is already open.'
    else
        while PORT=$(( $RANDOM % 10000 + 32768 ))
        do
            if ! port_bound "$PORT"  # Ensure ephemeral port is not already bound.
            then
                /bin/echo -n "Opening reverse tunnel on port $PORT..."
                open_tunnel "$PORT"
                if ! tunnel_exists
                then
                    /bin/echo -e 'not created.'
                else
                    /bin/echo -ne 'created.\nTesting tunnel...'
                    /usr/bin/sleep 3  # Give tunnel some time to open.
                    if ! port_bound "$PORT"
                    then
                        /bin/echo -e 'does not work.'
                    else
                        /bin/echo -e 'works.'
                    fi
                fi
                break  # Stop iterating through random ports.
            fi
        done
    fi
elif [ "$CMD" == 'stop' ]
then
    if ! tunnel_exists
    then
        /bin/echo 'Process not running.'
    else
        /bin/echo -n 'Killing process...'
        /usr/bin/pkill -f "ssh.*$USER@$HOST.*0.0.0.0:[0-9]{5}:127.0.0.1:$LOCAL_SSH" > /dev/null
        if tunnel_exists
        then
            /bin/echo 'process not killed.'
        else
            /bin/echo 'process killed.'
        fi
    fi
else
    /bin/echo 'Invalid command.'
fi
