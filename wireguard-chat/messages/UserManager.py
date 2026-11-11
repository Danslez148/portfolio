from messages.ServerMessageGenerator import ServerMessage

class UserManager:
    """Handles all interactions with users on the server. The controller will call these methods to send requests to the server, and this class will handle formatting the request and parsing the response."""
    def __init__(self, async_client):
        self.client = async_client

    async def setUsername(self, name: str) -> tuple[bool, str, str]:
        """Returns (success, new_name, error_msg)"""
        request = ServerMessage.setUsername(self.client.session_id, name)
        response = await self.client.send_request(request)
        
        # Check for error type (20) FIRST, because the server might return an error even if the channel exists
        if response.get('response_type') == 20:
            return False, "", response.get('error', 'Unknown error')
             
        if response.get('response_type') == 34: # RT_SET_USERNAME
            return True, response.get('new_username', name), ""
             
        return False, "", "Unexpected response from server."

    async def userList(self, offset: int = 0, channel: str = None) -> tuple[list, bool]:
        """Returns (users_list, has_next_page)"""
        request = ServerMessage.userList(self.client.session_id, channel, offset)
        response = await self.client.send_request(request)
        
        if response.get('response_type') == 20:
            return [], False
        return response.get('users', []), response.get('next_page', False)

    async def sendMessage(self, target: str, text: str) -> tuple[bool, str]:
        """Returns (success, error_msg)"""
        request = ServerMessage.userMessage(self.client.session_id, target, text)
        response = await self.client.send_request(request)
        
        if response.get('response_type') == 20:
            return False, response.get('error', 'Unknown error')
        return True, ""

    async def whoIs(self, username: str) -> dict:
        """Returns the WHOIS response dictionary for the queried username."""
        request = ServerMessage.whoIs(self.client.session_id, username)
        response = await self.client.send_request(request)
        return response