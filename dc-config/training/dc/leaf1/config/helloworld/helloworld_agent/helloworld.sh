#!/bin/bash

_term (){
    echo "Caught signal SIGTERM !! "
    # when SIGTERM is caught: kill the child process
    kill -TERM "$child" 2>/dev/null
}

# associate a handler with signal SIGTERM
trap _term SIGTERM

# set local variables
virtual_env="/opt/srlinux/python/virtual-env/bin/activate"
main_module="/etc/opt/srlinux/appmgr/helloworld_agent/helloworld_phase1.py"

# start python virtual environment
source "${virtual_env}"

# update PYTHONPATH variable with the agent directory and the SR Linux gRPC
export  PYTHONPATH="$PYTHONPATH:/etc/opt/srlinux/helper:/etc/opt/srlinux/appmgr/helloworld_agent:/opt/srlinux/bin:/usr/lib/python3.6/site-packages/sdk_protos"

# start the agent in the background (as a child process)
python3 ${main_module} &

# save its process id
child=$!

# wait for the child process to finish
wait "$child"

