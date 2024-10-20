import numpy as np
import py_libs.comm.message_pb2 as spb
from typing import Dict


def fromWeights(weights: spb.Weights) -> Dict[str, np.ndarray]:
    """
    将 Protobuf Weights 转换为 Python 字典，键为字符串，值为 numpy 数组。
    """
    # 使用列表中的权重项构建字典
    params = {
        entry.key: np.ndarray(
            shape=entry.value.shape,
            dtype=np.dtype(entry.value.dtype),
            buffer=entry.value.data
        )
        for entry in weights.weights
    }
    return params


def toWeights(params: Dict[str, np.ndarray]) -> spb.Weights:
    """
    将 Python 字典（键为字符串，值为 numpy 数组）转换为 Protobuf Weights。
    """
    weights = spb.Weights()

    # 遍历 Python 字典，将 numpy 数组转换为 NDArray 并添加到 weights
    for name, arr in params.items():
        nd_array = weights.weights[name]  # 获取 NDArray 的引用
        nd_array.dtype = str(arr.dtype)
        nd_array.shape.extend(arr.shape)
        nd_array.data = arr.tobytes()

    return weights
