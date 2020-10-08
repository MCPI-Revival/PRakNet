from praknet import messages

connected_ping = {
    "id": messages.ID_CONNECTED_PING,
    "time": None
}

unconnected_ping = {
    "id": messages.ID_UNCONNECTED_PING,
    "time": None,
    "magic": None,
    "client_guid": None
}

unconnected_ping_open_connections = {
    "id": messages.ID_UNCONNECTED_PING_OPEN_CONNECTIONS,
    "time": None,
    "magic": None,
    "client_guid": None
}

connected_pong = {
    "id": messages.ID_CONNECTED_PONG,
    "ping_time": None,
    "pong_time": None
}

open_connection_request_1 = {
    "id": messages.ID_OPEN_CONNECTION_REQUEST_1,
    "magic": None,
    "protocol_version": None,
    "mtu_size": None
}

open_connection_reply_1 = {
    "id": messages.ID_OPEN_CONNECTION_REPLY_1,
    "magic": None,
    "server_guid": None,
    "use_security": None,
    "mtu_size": None
}

open_connection_request_2 = {
    "id": messages.ID_OPEN_CONNECTION_REQUEST_2,
    "magic": None,
    "server_address": None,
    "mtu_size": None,
    "client_guid": None
}

open_connection_reply_2 = {
    "id": messages.ID_OPEN_CONNECTION_REPLY_2,
    "magic": None,
    "server_guid": None,
    "client_address": None,
    "mtu_size": None,
    "encryption_enabled": None
}

connection_request = {
    "id": messages.ID_CONNECTION_REQUEST,
    "client_guid": None,
    "request_time": None,
    "use_security": None
}

connection_request_accepted = {
    "id": messages.ID_CONNECTION_REQUEST_ACCEPTED,
    "client_address": None,
    "system_index": None,
    "system_addresses": [],
    "request_time": None,
    "time": None
}

connection_reply_accepted = {
    "id": messages.ID_CONNECTION_REPLY_ACCEPTED,
    
}

unconnected_pong = {
    "id": messages.ID_UNCONNECTED_PONG,
    "time": None,
    "server_guid": None,
    "magic": None,
    "data": None
}

advertise_system = {
    "id": messages.ID_ADVERTISE_SYSTEM,
    "time": None,
    "server_guid": None,
    "magic": None,
    "data": None
}