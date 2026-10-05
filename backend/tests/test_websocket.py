import json

def test_websocket_connection_and_ping(client):
    with client.websocket_connect("/ws/dashboard") as websocket:
        # Handshake message
        initial = websocket.receive_text()
        data = json.loads(initial)
        assert data["event"] == "CONNECTED"

        # Ping / Pong check
        websocket.send_text(json.dumps({"action": "PING"}))
        response = websocket.receive_text()
        pong = json.loads(response)
        assert pong["event"] == "PONG"
