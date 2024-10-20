import torch
from sympy.physics.vector.printing import params

from .callback_handler import CallbackHandlerBase
from py_libs.comm.bridge import Bridge
class CallbackHandlerPyt(CallbackHandlerBase):
    def __init__(self, model, device, print_weights=False):
        super().__init__(model)
        self.device = device
        self.print_weights = print_weights
        self.QF_Bridge = Bridge('mypipe.fifo')

    def on_epoch_end(self):
        # 发送模型参数
        self._do_sync()

    def _do_sync(self):
        local_param_dict = self._saveModelWeightsToDict()
        self.QF_Bridge.send_params(local_param_dict)
        weights = self.QF_Bridge.recv_params()
        print(weights)

    def _saveModelWeightsToDict(self):
        '''
        Pytorch specific implementation of abstract method
        _saveModelWeightsToDict in SwarmCallbackBase class.
        Saves the model passed to it inside its context, along with
        the list of key weightNames of model's weights.
        This is later used in the loadModel function for loading the
        updated set of weights as a flat dictionary
        '''
        inDict = {}
        self.weightNames = []
        model = self.model
        # in pytorch model weights are stored in a orderedDict
        # hence we dont need to ensure ordering, it should work as is.
        for wTensor in model.state_dict():
            # Hoewever weights are Tensors , we have change it to numpy types
            # wTensor is a str so we can use it as is.
            if (model.state_dict()[wTensor].is_cuda):
                #TypeError: can't convert cuda:0 device type tensor to numpy.
                #Use Tensor.cpu() to copy the tensor to host memory first.
                inDict[wTensor] = model.state_dict()[wTensor].cpu().numpy()
            else:
                inDict[wTensor] = model.state_dict()[wTensor].numpy()

            self.weightNames.append(wTensor)
        return inDict


    def _loadModelWeightsFromDict(self, inDict):
        '''
        Pytorch specific implementation of abstract method
        _loadModelWeightsFromDict in SwarmCallbackBase class.
        This function in tightly intertwined with saveModelWeightstoDict
        function, updating the same model that was passed to the last call
        of the save model function. Hence please use carefully
        :param inDict: The flat model weights' dictionary to be loaded in the model
        :return: Nothing is returned, the saved model is updated in-place
        '''
        # https://pytorch.org/tutorials/beginner/saving_loading_models.html
        # Partially loading a model or loading a partial model are common scenarios
        # when transfer learning or training a new complex model.
        # Leveraging trained parameters, even if only a few are usable,
        # will help to warmstart the training process and hopefully help your model
        # converge much faster than training from scratch.
        # Whether you are loading from a partial state_dict, which is missing some keys,
        # or loading a state_dict with more keys than the model that you are loading into,
        # you can set the strict argument to False in the load_state_dict() function
        # to ignore non-matching keys.

        model = self.model
        tempDict = {}
        for k in self.weightNames:
            tempDict[k] = torch.Tensor(inDict[k])
        model.load_state_dict(tempDict, strict=False)


        # IMP NOTE: model.train() or mode.eval or model.no_grads()
        # needs to be called by the caller, to ensure weights are
        # useful otherwise dropout, BatchNormalization may not work
        # as expected.
        # https://stackoverflow.com/questions/52945427/pytorch-manually-setting-weight-parameters-with-numpy-array-for-gru-lstm
        # https://stackoverflow.com/questions/60018578/what-does-model-eval-do-in-pytorch
        # use model.training to check status




    # def print_model_weights(self):
    #     print("\nModel weights at the end of the epoch:")
    #     for name, param in self.model.named_parameters():
    #         if param.requires_grad:
    #             original_data = param.data.clone()  # Clone the original data for demonstration
    #             modified_data = original_data * torch.rand_like(original_data)  # Example modification: random scaling
    #             param.data = modified_data  # Assign modified data back to the parameter
    #             print(f"Modified {name}: {param.data}\n")
    #

