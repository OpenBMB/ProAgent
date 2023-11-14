
from enum import Enum, auto, unique

@unique
class ENVIRONMENT(Enum):
    '''
    决定了 record cache 的访问形式
    - Development：不访问缓存，从头开始
    - Refine：访问缓存，但 user messages 必须一致，若不一致（例如节点返回值变化）则停止访问缓存
    - Production：无条件访问缓存，将 record 重播一遍
    '''
    # how to handle with different query？now it's loading the query defined in code instead of loading from cache.
    Development = auto() # ok
    Refine = auto() # ok
    Production = auto() # ok

