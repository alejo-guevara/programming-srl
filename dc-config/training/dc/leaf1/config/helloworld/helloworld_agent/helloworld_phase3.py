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
import json

import sdk_service_pb2
import sdk_service_pb2_grpc
import config_service_pb2
import telemetry_service_pb2
import telemetry_service_pb2_grpc
import route_service_pb2
import route_service_pb2_grpc
import nexthop_group_service_pb2
import nexthop_group_service_pb2_grpc
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
## and create an SDK service client stub
## and create an SDK notification service stub
############################################################

channel = grpc.insecure_channel('127.0.0.1:50053')
stub = sdk_service_pb2_grpc.SdkMgrServiceStub(channel)
sdk_notification_service_client = sdk_service_pb2_grpc.SdkNotificationServiceStub(channel)

## Verify that SIGTERM signal was received
sigterm_exit = False

## validate an IPv4 address
def validateIPv4Network(i):
   try:
       if ipaddress.IPv4Network(i):
           return True
   except ValueError as err:
       return False


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

        # unregister agent
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

#####################################
## Create an SDK notification stream
#####################################
def create_sdk_stream():

    # build Create request
    op = sdk_service_pb2.NotificationRegisterRequest.Create
    request=sdk_service_pb2.NotificationRegisterRequest(op=op)

    # call SDK RPC to create a new stream
    notification_response = stub.NotificationRegister(
        request=request,
        metadata=metadata)

    # process the response, return stream ID if successful
    if notification_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Notification Stream Create failed with error {notification_response.error_str}")
        return 0
    else:
        logging.info(f"Notification Stream successful. stream ID: {notification_response.stream_id}, sub ID: {notification_response.sub_id}")
        return notification_response.stream_id

#########################################################
## Use notification stream to subscribe to 'config events
#########################################################
def add_sdk_config_subscription(stream_id):

    # Build subscription request for config events
    subs_request=sdk_service_pb2.NotificationRegisterRequest(
        op=sdk_service_pb2.NotificationRegisterRequest.AddSubscription,
        stream_id=stream_id,
        config=config_service_pb2.ConfigSubscriptionRequest())

    # Call RPC
    subscription_response = stub.NotificationRegister(
        request=subs_request,
        metadata=metadata)


    # Process response
    if subscription_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error("Config Subscription failed")
    else:
        logging.info(f"Config Subscription successful. stream ID: {subscription_response.stream_id}, sub ID: {subscription_response.sub_id}")
    return

#########################################################
## Use notification stream to subscribe to 'config events
#########################################################
def add_sdk_ip_route_subscription(stream_id):

    # Build subscription request for config events
    subs_request=sdk_service_pb2.NotificationRegisterRequest(
        op=sdk_service_pb2.NotificationRegisterRequest.AddSubscription,
        stream_id=stream_id,
        route=route_service_pb2.IpRouteSubscriptionRequest())

    # Call RPC
    subscription_response = stub.NotificationRegister(
        request=subs_request,
        metadata=metadata)


    # Process response
    if subscription_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error("Config Subscription failed")
    else:
        logging.info(f"Config Subscription successful. stream ID: {subscription_response.stream_id}, sub ID: {subscription_response.sub_id}")
    return


########################################################
## Start notification stream from SDK SR Linux
#########################################################
def start_notification_stream(stream_id):

    # Build request
    request=sdk_service_pb2.NotificationStreamRequest(stream_id=stream_id)

    # Call Server Streaming SDK service
    # SR Linux will start streamning requested notifications
    notification_stream = sdk_notification_service_client.NotificationStream(
        request=request,
        metadata=metadata)

    # return the stream
    return notification_stream


########################################################
## Process the received notification stream
## Only config events are expected
## Exit the loop if SIGTERM is received
#########################################################
def process_notification(notification):
    for obj in notification.notification:
        if obj.HasField("config"):
            ## Process config notification
            logging.info("--> Received config notification")
            process_config_notification(obj)
        elif obj.HasField("route"):
            logging.info("--> Received ip route notification")
            ## Do nothing - the notification was displayed by the calling function
        else:
            logging.info("--> Received unexpected notification")
        if sigterm_exit:
            ## exit loop if agent has been stopped
            logging.info("Agent Stopped Time :: {}".format(datetime.datetime.now()))
            return

############################################################
## update a object in the state datastore
## using the telemetry grpc service
## Input parameters:
## - js_path: JSON Path = the base YANG container
## - js_data: JSON attribute/value pair(s) based on the YANG model
############################################################
def update_state_datastore(js_path, js_data ):

    # create gRPC client stub for the Telemetry Service
    telemetry_stub = telemetry_service_pb2_grpc.SdkMgrTelemetryServiceStub(channel)

    # Build an telemetry update service request
    telemetry_update_request = telemetry_service_pb2.TelemetryUpdateRequest()

    # Add the YANG Path and Attribute/Value pair to the request
    telemetry_info = telemetry_update_request.state.add()
    telemetry_info.key.js_path = js_path
    telemetry_info.data.json_content = js_data

    # Log the request
    logging.info(f"Telemetry_Update_Request ::\n{telemetry_update_request}")

    # Call the telemetry RPC
    telemetry_response = telemetry_stub.TelemetryAddOrUpdate(
        request=telemetry_update_request,
        metadata=metadata)

    return telemetry_response

########################################################
## Create a next-hop group
## In:
## - nhg_name: the name of the NHG
## - nw_instance: the network instance in which the route is created
## - resolve_to: resolve to type (LOCAL, DIRECT or INDIRECT)
## - resolution_type: resolution type (REGULAR or MPLS)
## - next_hop_list: a list of one or more netxh hops
#########################################################
def create_next_hop_group(nhg_name, nw_instance, resolve_to, resolution_type, next_hop_list):
    nhg_stub = nexthop_group_service_pb2_grpc.SdkMgrNextHopGroupServiceStub(channel)
    nhg_request = nexthop_group_service_pb2.NextHopGroupRequest()
    nhg_info = nhg_request.group_info.add()
    nhg_info.key.name = nhg_name
    nhg_info.key.network_instance_name = nw_instance
    for next_hop_ip in next_hop_list:
        nh = nhg_info.data.next_hop.add()
        nh.type = resolution_type
        nh.resolve_to = resolve_to
        nh.ip_nexthop.addr = ipaddress.ip_address(next_hop_ip).packed

    nhg_response = nhg_stub.NextHopGroupAddOrUpdate(request=nhg_request, metadata=metadata)
    if nhg_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"NHG addition failed for {nhg_name} with error {nhg_response.error_str}")

########################################################
## Create a new static route to the routing table
## In:
## - nw_instance: the network instance in which the route is created
## - ip_prefix: the ip address of the static route w/o mask
## - ip_prefix_length: the mask length
## - nhg_name: the next group for this static IP
## - preference: the preference value of the static route
## - metric: the metric of the static route
#########################################################
def create_static_route(nw_instance, ip_prefix, ip_prefix_length, nhg_name,
                        preference=None, metric=None):
    route_stub = route_service_pb2_grpc.SdkMgrRouteServiceStub(channel)
    route_request = route_service_pb2.RouteAddRequest()
    route_info = route_request.routes.add()
    route_info.key.net_inst_name = nw_instance
    route_info.key.ip_prefix.ip_addr.addr = ipaddress.ip_address(ip_prefix).packed
    route_info.key.ip_prefix.prefix_length = ip_prefix_length
    route_info.data.nexthop_group_name = nhg_name
    if preference is not None:
        route_info.data.preference = preference
    if metric is not None:
        route_info.data.metric = metric
    route_response = route_stub.RouteAddOrUpdate(request=route_request, metadata=metadata)
    if route_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Route {ip_prefix}/{ip_prefix_length} addition failed with error {route_response.error_str}")


########################################################
## Process specifically a config notification
## Expects that 'name' from 'helloworld' branch has been configured
## Will set 'response' string as a response
#########################################################
def process_config_notification(obj):

    # Convert received JSON string into a dictionary
    data = json.loads(obj.config.data.json)
    logging.info(f"Data :: {data}" )

    # Check if the expected 'name' filed is present
    if 'name' in data:

        # extract its value from dictionary
        firstname = data['name']['value']

        # use it to build the response
        hello_string = "Hello, " + firstname

        # set the 'response' field as a JSON dict
        json_content={"response": {"value": hello_string }}

        # call the telemetry RPC to update the state datastore
        # the json dict must be converted back to a JSON string
        update_state_datastore( js_path='.helloworld',
                                js_data=json.dumps(json_content))

    if 'ip_address' in data:
        logging.info("we have an ip address")
        ipa = data['ip_address']['value']
        if validateIPv4Network(ipa):
            logging.info(f"we have a valid ip address: {ipa}")

            # convert string to ipaddress object
            ipnetwork = ipaddress.IPv4Network(ipa)

            ## create a new nexthop group "nhg_SDK" in the "default" network instance
            ## the next hop group will have two next hops (spine1 and spine2)
            create_next_hop_group(
                "nhg_SDK",
                "default",
                nexthop_group_service_pb2.NextHop.ResolveToType.Value("DIRECT"),
                nexthop_group_service_pb2.NextHop.ResolutionType.Value("REGULAR"),
                next_hop_list=["10.1.2.0", "10.2.2.0"])

            ## now create a static route for the ipaddress using the above next hop group
            create_static_route(
                "default",
                ipnetwork.network_address,
                ipnetwork.prefixlen,
                "nhg_SDK")

        else:
            logging.info(f"{ipaddress} is not a valid IP address")


## Main agent function
def run_agent():

    ## Register Agent
    register_request = sdk_service_pb2.AgentRegistrationRequest()
    register_request.agent_liveliness=10
    register_response = stub.AgentRegister(request=register_request, metadata=metadata)
    if register_response.status == sdk_common_pb2.SdkMgrStatus.Value("kSdkMgrFailed"):
        logging.error(f"Agent Registration failed with error {register_response.error_str}")
    else:
        logging.info(f"Agent Registration successful. App ID: {register_response.app_id}")

    app_id = register_response.app_id

    ## Start separate thread to send keep alive every 10 seconds
    thread = threading.Thread(target=send_keep_alive)
    thread.start()

    ## Create a new SDK notification stream
    stream_id = create_sdk_stream()

    ## Subscribe to 'config' notifications
    ## Only configuration of helloworld YANG data models will be received
    ## And only once they are commit into the running configuration
    add_sdk_config_subscription(stream_id)

    ## and subscribe to ip route notifications
    add_sdk_ip_route_subscription(stream_id)

    ## Start listening for notifications from SR Linux
    notification_stream  = start_notification_stream(stream_id)

    ## process received notifications
    for notification in notification_stream:
        logging.info(f"Received Notification ::\n{notification}")
        process_notification(notification)


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


