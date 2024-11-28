# Marvel Service

A gRPC-based service to fetch Marvel characters using the Marvel API, with caching for enhanced performance.

---

## Features

- Fetch Marvel characters via gRPC.
- Caching for optimized API calls.
- Handles API responses (200, 304).
- Error handling with detailed logging.

---

## Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/7kfpun/kchallenge.git
   cd kchallenge
   ```

2. **Install Dependencies**:
	```bash
	pip install -r requirements.txt
	```

3. **Generate gRPC Code (if needed)**:
	```bash
	python3 -m grpc_tools.protoc -I app/grpc_services/proto --python_out=app/grpc_services/proto --grpc_python_out=app/grpc_services/proto app/grpc_services/proto/marvel.protomarvel.proto
	```

4. **Run the Server**:
	```bash
	python3 server.py
	```
	
## Tests

Run tests with:
```bash
python3 -m unittest discover tests
```
