#!/usr/bin/env python
# coding=utf-8

import grpc
import datetime
import sys
import logging
import socket
import os
import ipaddress
import signal
import time
import threading

import appid_service_pb2
import sdk_service_pb2
import sdk_service_pb2_grpc
import lldp_service_pb2
import interface_service_pb2
import networkinstance_service_pb2
import bfd_service_pb2
import route_service_pb2
import route_service_pb2_grpc
import nexthop_group_service_pb2
import nexthop_group_service_pb2_grpc
import mpls_service_pb2
import mpls_service_pb2_grpc
import config_service_pb2
import telemetry_service_pb2
import telemetry_service_pb2_grpc
import sdk_common_pb2

############################################################
## Agent will start with this name
############################################################
agent_name = 'helloworld'
metadata = [('agent_name', agent_name)]

############################################################
## Global parameters:
## Open a GRPC channel to connect to the SR Linux sdk_mgr
## sdk_mgr will be listening on 50053
## and create a gRPC client stub
############################################################

channel = grpc.insecure_channel('127.0.0.1:50053')
stub = sdk_service_pb2_grpc.SdkMgrServiceStub(channel)

## Verify that SIGTERM signal was received
sigterm_exit = False


############################################################
## Gracefully handle SIGTERM signal (SIGTERM number = 15)
## When called, will unregister Agent and gracefully exit
############################################################
def exit_gracefully(signum, frame):
    logging.info("Caught signal :: {}\n will unregister helloworld agent".format(signum))
    try:
        global sigterm_exit
        sigterm_exit = True
        logging.info(f"Unregister Agent")
        unregister_request = sdk_service_pb2.AgentRegistrationRequest()
        unregister_response = stub.AgentUnRegister(request=unregister_request, metadata=metadata)
        logging.info(f"Unregister response:: {sdk_common_pb2.SdkMgrStatus.Name(unregister_response.status)}")
    except grpc._channel._Rendezvous as err:
        logging.error('GOING TO EXIT NOW: {}'.format(err))
        sys.exit()

## Keep Alive thread: send a keep every 10 seconds via gRPC call
def send_keep_alive():
    ## exit the thread when sigterm is received
    while not sigterm_exit:
        logging.info("Send Keep Alive")
        keepalive_request = sdk_service_pb2.KeepAliveRequest()
        keepalive_response = stub.KeepAlive(request=keepalive_request, metadata=metadata)
        if keepalive_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
            logging.error("Keep Alive failed")
        time.sleep(10)

## Agent function
def run_agent():

    ## Register Agent
    register_request = sdk_service_pb2.AgentRegistrationRequest()
    register_request.agent_liveliness=10
    register_response = stub.AgentRegister(request=register_request, metadata=metadata)
    if register_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Agent Registration failed with error {register_response.error_str}")
    else:
        logging.info(f"Agent Registration successful. App ID: {register_response.app_id}")

    ## Start separate thread to send keep alive every 10 seconds
    thread = threading.Thread(target=send_keep_alive)
    thread.start()

    ## Wait for signals
    while True:
        # suspend process until signal caught
        signal.pause()
        if sigterm_exit:
            logging.info("Agent Stopped Time :: {}".format(datetime.datetime.now()))
            break


if __name__ == '__main__':

    ## configure SIGTERM handler
    signal.signal(signal.SIGTERM, exit_gracefully)

    ## configure log file
    log_filename = '/var/log/srlinux/stdout/hello.log'
    logging.basicConfig(filename=log_filename, filemode='w',datefmt='%H:%M:%S', level=logging.INFO)
    logging.info("Agent Start Time :: {}".format(datetime.datetime.now()))

    ## Run agent function
    run_agent()
    sys.exit()

