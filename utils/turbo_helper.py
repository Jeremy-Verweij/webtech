from h11 import ConnectionClosed
import turbo_flask
from setup import turbo
from flask import session

session_id_to_turbo_id = {}

def turbo_user_id_init():
    @turbo.user_id
    def get_user_id():
        id = turbo.default_user_id()
        
        if "user_id" in session:
            session_id_to_turbo_id[session["user_id"]] = id
            
        return id

def push_except(self:turbo_flask, stream, not_to=[]):
        """Push a turbo stream update over WebSocket to one or more clients.

        :param stream: one or a list of stream updates generated by the
                       ``append()``, ``prepend()``, ``replace()``, ``update()``
                       and ``remove()`` methods.
        :param to: the id of the target client. Set to ``None`` to send to all
                   connected clients, or to a list of ids to target multiple
                   clients.
        """
        
        to = self.clients.keys()
        
        for recipient in to:
            if recipient not in not_to:
                for ws in self.clients[recipient]:
                    try:
                        ws.send(stream)
                    except (BrokenPipeError, ConnectionClosed):  # pragma: no cover
                        pass