#!/bin/bash

CMD=$1
USER=$2
IP=$3
fw_cmd () { /bin/echo /usr/bin/ssh "$USER@$IP" "/usr/bin/firewall-cmd --add-port=$1/tcp"; }
ssh_cmd () { /bin/echo /usr/bin/ssh -N -R 0.0.0.0:$1:127.0.0.1:22 "$USER@$IP" $2; }
nc_cmd () { /bin/echo /bin/nc -nvz $IP $PORT; }
if [ "$CMD" == "start" ]
then
    if ! /usr/bin/pgrep -f -x "`ssh_cmd '[0-9]*?'`" > /dev/null
    then
        /bin/echo "Opening reverse SSH tunnel..."
        while
        PORT=$(( $RANDOM % 10000 + 32768 ))
        do
            if ! `nc_cmd` > /dev/null 2>&1
                then
                /bin/echo "Using port $PORT..."
                if `fw_cmd $PORT` > /dev/null 
                then
                    /bin/echo "Rule added. Opening tunnel..."
                    eval "`ssh_cmd $PORT \&`"
                    if /usr/bin/pgrep -f -x "`ssh_cmd '[0-9]*?'`" > /dev/null
                    then
                        /bin/echo "Process created. Testing tunnel..."
                        /bin/sleep 10
                        if ! `nc_cmd`
                        then
                            /bin/echo "Something went wrong. Tunnel not created."
                        fi
                    else
                        /bin/echo "Something went wrong. Process not created."
                    fi
                else
                    /bin/echo "Something went wrong. Rule not added."
                fi
                break
            fi
        done
    else
        /bin/echo "Tunnel is already open."
    fi
elif [ "$CMD" == "stop" ]
then
    if /usr/bin/pgrep -f -x "`ssh_cmd '[0-9]*?'`" > /dev/null
    then
        /bin/echo "Process found. Killing process..."
        /usr/bin/pkill -f -x "`ssh_cmd '[0-9]*?'`"
        /bin/sleep 3
        if ! /usr/bin/pgrep -f -x "`ssh_cmd '[0-9]*?'`" > /dev/null
        then
            /bin/echo "Process killed."
        else
            /bin/echo "Something went wrong. Process not killed."
        fi
    else
        /bin/echo "Process not running."
    fi
else
    /bin/echo "Invalid command."
fi

