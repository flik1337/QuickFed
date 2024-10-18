import torch
from .callback_handler import CallbackHandlerBase

class CallbackHandlerPyt(CallbackHandlerBase):
    def __init__(self, model, device, print_weights=False):
        super().__init__(model)
        self.device = device
        self.print_weights = print_weights

    def on_epoch_end(self):
        if self.print_weights:
            self.print_model_weights()

    def print_model_weights(self):
        print("\nModel weights at the end of the epoch:")
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                original_data = param.data.clone()  # Clone the original data for demonstration
                modified_data = original_data * torch.rand_like(original_data)  # Example modification: random scaling
                param.data = modified_data  # Assign modified data back to the parameter
                print(f"Modified {name}: {param.data}\n")


