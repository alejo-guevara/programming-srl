import grpc

import helloworld_pb2
import helloworld_pb2_grpc


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        print("Got request from %s" % request.name)
        print("The received message is:")
        print(request)
        message='Hello, %s %s!' % (request.data.title, request.name)
        return helloworld_pb2.HelloReply(message=message)

    def SayStreambackHello(self, request, context):
        print("Streamback: Received message: {}".format(request))
        for i in range(request.data.number_of_replies):
            print("-- Process reply #%i" % (i))
            message='Streamed reply #%i: Hello, %s %s!' % (i+1,request.data.title, request.name)
            yield helloworld_pb2.HelloReply(message=message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()

