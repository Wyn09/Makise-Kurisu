import time
class SharedState:
    def __init__(self):
        self.user_input = None
        self.user_last_input_time = 0.0
       

SHARE_STATE = SharedState()