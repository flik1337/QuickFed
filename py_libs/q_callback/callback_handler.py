class CallbackHandlerBase:
    def __init__(self, model):
        self.model = model

    def on_epoch_end(self):
        raise NotImplementedError("This method should be overridden by subclasses.")