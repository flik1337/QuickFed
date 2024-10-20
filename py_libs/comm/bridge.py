import os
import numpy as np
from pathlib import Path
from datetime import datetime
from numpy import number
import time
# from message_pb2 import Header, Weights
import py_libs.comm.message_pb2 as mpb
from py_libs.comm.param_util import fromWeights,toWeights

northBoundMode="rb"
southBoundMode="wb"

NorthBound = 1
SouthBound = 2

class Bridge:
    def __init__(self, fifo_name: str):
        """初始化 Bridge 并打开 FIFO 管道。"""
        # self.fifo_path = (Path(__file__).parent / fifo_name).resolve().as_posix()
        # self.fifo_path = (Path(__file__).parent / fifo_name).resolve()

        # self.ensure_fifo_exists()
        self.fifo_fd = None # 初始化管道流

        self._createPipes = True
        self._lanes = {}
        self._openLanes = {} # 读写管道

        self._makeBridgeLanes()
        self._openBridgeLanes() # fixme: 死锁

        self._serializedHeaderSiz = 0

    def _openBridgeLanes(self):

        def openLane(direction, mode) -> None:
            # self.__logIt(f"Opening [{direction}] = <{self._lanes[direction]}> in <{mode}> mode")
            self._openLanes[direction] = open(self._lanes[direction], mode)
            return

        openLane(NorthBound, northBoundMode)
        openLane(SouthBound, southBoundMode)
        return

    def _makeBridgeLanes(self) -> None:
        def getPath(envvar: str) -> str:
            return (Path(__file__).parent / (envvar + '.fifo')).resolve().as_posix()


        def makeLane(lane: str, direction: int) -> None:
            try:
                self._lanes[direction] = lane
                # self.__logIt(f"Creating [{direction}] = <{self._lanes[direction]}>")
                if (self._createPipes):
                    os.mkfifo(lane, 0o777)
                    self.__logIt(f"{lane}: pipe created")
                else:
                    while (not (os.path.exists(lane))):
                        self.__logIt(f"{lane}: waiting for pipes to be created")
                        time.sleep(1)
                # self.__logIt(f"Created [{direction}] = <{self._lanes[direction]}>")

            except FileExistsError:
                self.__logIt(f"{lane}: File exists")
            except BaseException as be:
                self.__logIt(f"{lane}: {be}")

        # The default umask seems to be 022. It is applied to the mode specified
        # in mkfifo. Therefore, even though we ask for 777, what we actually get
        # is 755. This prevents the two ends of the bridge from having different
        # user IDs - the second party will not have the requisite permissions to
        # open the FIFO is write mode. We workaround this by disabling the mask,
        # creating the pipes, and then, restoring the mask.
        currMask = os.umask(0)

        makeLane(getPath("SL_REQUEST_CHANNEL"), SouthBound)
        makeLane(getPath("SL_RESPONSE_CHANNEL"), NorthBound)

        os.umask(currMask)

    def __logIt(self, *args, **kwargs):
        print(datetime.now().isoformat(), *args, **kwargs, flush=True)
        return

    def ensure_fifo_exists(self):
        """确保 FIFO 文件存在，如果不存在则创建。"""
        if not self.fifo_path.exists():
            os.mkfifo(self.fifo_path)
            print(f"FIFO created at {self.fifo_path}")
        else:
            print(f"FIFO already exists at {self.fifo_path}")


    def send_params(self, params):
        """发送序列化后的模型参数。"""
        weights = toWeights(params)
        serialized_message = weights.SerializeToString()
        self._serializedHeaderSiz = len(serialized_message)
        lane = self._openLanes[1] # south
        lane.write(serialized_message)
        lane.flush()
        print("Message sent")

    def _read(self, recvLane, nBytes: int) -> bytes:
        lane = self._openLanes[recvLane]
        msg = lane.read(nBytes)
        if len(msg) != nBytes:
            raise RuntimeError(
                f"wanted: {nBytes} bytes, got {len(msg)} bytes: pipe closed?"
            )

        return msg

    def recv_params(self):
        """接收并反序列化模型参数。"""
        serialized_data = self._read(2,self._serializedHeaderSiz)  # Adjust buffer size as necessary
        weights = mpb.Weights()
        weights.ParseFromString(serialized_data)
        self.close_fifo()
        return fromWeights(weights)

    def to_weights(self, params):
        """将字典转换为 Protobuf 的 Weights 对象。"""
        weights = mpb.Weights()
        for key, value in params.items():
            entry = weights.weights.add()
            entry.key = key
            entry.value.dtype = str(value.dtype)
            entry.value.shape.extend(value.shape)
            entry.value.data = value.tobytes()
        return weights

    def from_weights(self, weights):
        """将 Protobuf 的 Weights 对象转换为字典。"""
        return {
            entry.key: np.frombuffer(entry.value.data, dtype=np.dtype(entry.value.dtype)).reshape(entry.value.shape)
            for entry in weights.weights
        }

