from messages.ServerMessageGenerator import ServerMessage

class ChannelManager:
    """Handles all interactions with channels on the server. The controller will call these methods to send requests to the server, and this class will handle formatting the request and parsing the response."""
    def __init__(self, async_client):
        self.client = async_client

    async def joinChannel(self, name: str) -> tuple[bool, str, str]:
        """Returns (success, description, error_msg)"""
        request = ServerMessage.channelJoin(self.client.session_id, name)
        response = await self.client.send_request(request)
        
        # Check for error type (20) FIRST, because the server might return an error even if the channel exists
        if response.get('response_type') == 20:
            return False, "", response.get('error', 'Unknown error')
            
        if response.get('response_type') == 28:
            return True, response.get('description', ''), ""
            
        return False, "", "Unexpected response from server."

    async def createChannel(self, name: str, description: str) -> tuple[bool, str]:
        """Returns (success, error_msg)"""
        request = ServerMessage.channelCreate(self.client.session_id, name, description)
        response = await self.client.send_request(request)
        
        if response.get('response_type') == 20:
            return False, response.get('error', 'Unknown error')
            
        if response.get('response_type') == 25: # RT_CHANNEL_CREATE
            return True, ""
            
        return False, "Unexpected response from server."

    async def sendMessage(self, channel: str, text: str) -> tuple[bool, str]:
        """Returns (success, error_msg)"""
        request = ServerMessage.channelMessage(self.client.session_id, channel, text)
        response = await self.client.send_request(request)
        
        if response.get('response_type') == 20:
            return False, response.get('error', 'Unknown error')
        return True, ""

    async def leaveChannel(self, channel: str):
        """No return value, since we're leaving the channel anyway. Errors are logged but not raised."""
        request = ServerMessage.channelLeave(self.client.session_id, channel)
        await self.client.send_request(request) #don't care if leaving fails

    async def listChannels(self, offset: int = 0) -> tuple[list, bool]:
        """Returns (channel_list, has_next_page)"""
        request = ServerMessage.channelList(self.client.session_id, offset)
        response = await self.client.send_request(request)
        
        if response.get('response_type') == 20:
            return [], False
        return response.get('channels', []), response.get('next_page', False)

    async def getChannelInfo(self, channel: str) -> tuple[str, str]:
        """Returns (description, error_msg)"""
        request = ServerMessage.channelInfo(self.client.session_id, channel)
        response = await self.client.send_request(request)
         
        if response.get('response_type') == 20:
            return "", response.get('error', 'Unknown error')
        return response.get('description', ''), ""