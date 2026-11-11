import random

class ServerMessage:
    """Generates the standard protocol dictionaries (as specified on https://csc4026z.link/chat_messages/session/)for the chat client so it can communicate with the server."""
    
    @staticmethod
    def _generate_handle() -> int:
        """Generates a random request handle for each message. This is required by the server for matching requests and responses, but the client doesn't need to do anything with it since the client will just wait for the next response after sending a request. The server doesn't require handles to be unique, so we can just generate a random one each time without keeping track of them."""
        return random.randrange(0, 2**32) # generates a random 32-bit integer for request handles (for some reason we should always include this)


# Session messages
    @classmethod
    def connect(cls) -> dict:
        """Returns the dictionary for the initial connect request. No session ID is included since we don't have one yet."""
        return {
            'request_type': 1,
            'request_handle': cls._generate_handle() } # creates the dictionary for initial connect request

    @classmethod
    def ping(cls, session_id: int) -> dict:
        """Returns the dictionary for a ping request, which includes the session ID so the server knows which session to keep alive."""
        return {
            'request_type': 3,
            'session': session_id,
            'request_handle': cls._generate_handle() } #creates the dictionary for ping requests (this will have to be generated often so the server doesnt time out)

    @classmethod
    def disconnect(cls, session_id: int) -> dict:
        """Returns the dictionary for a disconnect request, which includes the session ID so the server knows which session to disconnect."""
        return {
            'request_type': 2,
            'session': session_id,
            'request_handle': cls._generate_handle() } #create the dictionary for disconnect requests
    
# Channel Messages
    @classmethod
    def channelCreate(cls, session_id: int, channel_name: str, channel_description: str) -> dict:
        """Returns the dictionary for a channel creation request."""
        return {
            'request_type': 4,
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'channel': channel_name,
            'description': channel_description } #create the dictionary for channel creation requests
    
    @classmethod
    def channelList(cls, session_id: int, offset: int = 0) -> dict:
        """Returns the dictionary for a channel list request. The offset parameter is optional and can be used for pagination if there are more than 10 channels."""
        request = {
            'request_type': 5, 
            'session': session_id,
            'request_handle': cls._generate_handle() }
        
        # Logic if there is more than 10 channels 
        # still have to code this in 
        # (have to check the response for the the next_page flag and then decide if we need to send another request with an offset)
        if offset > 0:
            request['offset'] = offset
            
        return request

    @classmethod
    def channelInfo(cls, session_id: int, channel_name: str) -> dict:
        """Returns the dictionary for a channel info request, which asks for the description of a channel."""
        return {
            'request_type': 6, # [cite: 659]
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'channel': channel_name[:20] }

    @classmethod
    def channelJoin(cls, session_id: int, channel_name: str) -> dict:
        """Returns the dictionary for a channel join request."""
        return {
            'request_type': 7, # [cite: 687]
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'channel': channel_name[:20] }

    @classmethod
    def channelLeave(cls, session_id: int, channel_name: str) -> dict:
        """Returns the dictionary for a channel leave request."""
        return {
            'request_type': 8, # [cite: 722]
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'channel': channel_name[:20] }

    @classmethod
    def channelMessage(cls, session_id: int, channel_name: str, message: str) -> dict:
        """Returns the dictionary for a channel message request."""
        return {
            'request_type': 9,
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'channel': channel_name[:20],
            'message': message[:500] }
    
    # User messages
    @classmethod
    def setUsername(cls, session_id: int, username: str) -> dict:
        """Returns the dictionary for a set username request."""
        return {
            'request_type': 13,
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'username': username[:20]
        }

    @classmethod
    def userList(cls, session_id: int, channel: str = None, offset: int = 0) -> dict: #set channel to none, so we can optionally add it if a user asks for it
        """Returns the dictionary for a user list request. If channel is specified, it will list users in that channel. If channel is None, it will list all users."""
        request = {
            'request_type': 14,
            'session': session_id,
            'request_handle': cls._generate_handle()
        }
        
        # 'channel' and 'offset' are optional fields for this request
        if channel != None:
            request['channel'] = channel[:20]
        if offset > 0:
            request['offset'] = offset
            
        return request

    @classmethod
    def userMessage(cls, session_id: int, to_username: str, message: str) -> dict:
        """Returns the dictionary for a user message request."""
        return {
            'request_type': 12,
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'to_username': to_username[:20],
            'message': message[:500]
        }

    @classmethod
    def whoAmI(cls, session_id: int) -> dict:
        """Returns the dictionary for a who am I request."""
        return {
            'request_type': 11,
            'session': session_id,
            'request_handle': cls._generate_handle()
        }

    @classmethod
    def whoIs(cls, session_id: int, username: str) -> dict:
        """Returns the dictionary for a who is request, which asks for the channels that a user is in."""
        return {
            'request_type': 10,
            'session': session_id,
            'request_handle': cls._generate_handle(),
            'username': username[:20]
        }