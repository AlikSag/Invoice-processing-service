"""Command-line client for all five invoice RPCs."""
import argparse
import json
from pathlib import Path
import time

import grpc
from google.protobuf.json_format import MessageToDict

from grpc_service import invoice_service_pb2 as pb
from grpc_service import invoice_service_pb2_grpc as rpc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", default="127.0.0.1:50051")

    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("pdf", type=Path)

    for name in ("status", "result", "delete"):
        commands.add_parser(name).add_argument("req_no")
    commands.add_parser("list")
    demo = commands.add_parser("demo", help="Create a job and poll until DONE or FAILED")
    demo.add_argument("pdf", type=Path)
    demo.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()

    with grpc.insecure_channel(args.address) as channel:
        stub = rpc.InvoiceServiceStub(channel)
        try:
            if args.command in ("create", "demo"):
                response = stub.CreateJob(pb.CreateJobRequest(
                    filename=args.pdf.name, file_content=args.pdf.read_bytes()
                ), timeout=30)
                print(json.dumps(MessageToDict(response)))
                if args.command == "create":
                    return
                request = pb.JobRequest(req_no=response.req_no)
                deadline = time.monotonic() + args.timeout
                previous_state = response.state
                while time.monotonic() < deadline:
                    response = stub.GetJobStatus(request, timeout=10)
                    if response.state != previous_state:
                        print(json.dumps(MessageToDict(response)))
                        previous_state = response.state
                    if response.state in ("DONE", "FAILED"):
                        result = stub.GetJobResult(request, timeout=10)
                        print(json.dumps(MessageToDict(result), indent=2))
                        if response.state == "FAILED":
                            raise SystemExit(1)
                        return
                    time.sleep(0.2)
                parser.exit(1, "Timed out waiting for job completion\n")
            elif args.command == "list":
                response = stub.ListJobs(pb.Empty(), timeout=10)
            else:
                method = {"status": stub.GetJobStatus, "result": stub.GetJobResult,
                          "delete": stub.DeleteJob}[args.command]
                response = method(pb.JobRequest(req_no=args.req_no), timeout=10)
            print(json.dumps(MessageToDict(response), indent=2))
        except (grpc.RpcError, OSError) as error:
            parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
