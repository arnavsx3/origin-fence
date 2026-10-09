"""A controlled agent-originated outbound connection attempt for the demo."""

import socket

socket.create_connection(("127.0.0.1", 65534), timeout=1)
