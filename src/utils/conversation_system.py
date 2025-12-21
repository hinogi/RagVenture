class ConversationSystem:
    
    def __init__(self):
        self.pending_question = None

    def has_pending_question(self):
        return self.pending_question