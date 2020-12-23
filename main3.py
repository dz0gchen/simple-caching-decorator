import time
from typing import Union, Dict
from datetime import datetime
from multiprocessing import Process, Manager

DELTASEC = 2


def cache(limit=10):
    def decorate(f):
        def wrapper(self, key, value=None, limit=limit):
            if f.__name__ == "set":
                if len(self.cache) == limit:
                    self.cache.clear()
                    print("clear cache")
                self.cache[key] = (value, datetime.now())
                print("load into cache")
                return f(self, key, value)
            else:
                val = self.cache.get(key)
                if val is not None:
                    data, _ = val
                    print("load from cache")
                    return data
            return f(self, key)
        return wrapper
    return decorate


class MyStore(dict):
    """
    Эмуляция key-value storage на основе словаря.
    """
    def __init__(self, cache):
        self.cache = cache

    @cache(100)
    def set(self, key: Union[int, str], value: Union[int, str]):
        print("set data to store")
        return dict.__setitem__(self, key, value)

    @cache()
    def get(self, key: Union[int, str]):
        print("cache is not used")
        return dict.__getitem__(self, key)

    def __getattribute__(self, attr):
        """
        Убираем лишние методы из словаря, согласно спецификации storage
        может иметь только set/get методы.
        """
        if attr in MyStore.__dict__ or self.__dict__ or \
                dict.__dict__[attr].__name__ in ["__getitem__", "__setitem__"]:
            return super(dict, self).__getattribute__(attr)
        else:
            raise AttributeError


def main():
    def flow(store: MyStore):
        store.set(3, 4)
        time.sleep(4)
        store.get(3)
        store.set("ddd", 56)
        store.get("ddd")
        time.sleep(4)

    def cleaning(cache: Dict):
        while True:
            try:
                iter(cache.items())
            except TypeError:
                print("waiting data in cache")
                time.sleep(3)
                continue
            for key,value in cache.items():
                _, stamp = value
                if int((datetime.now() - stamp).total_seconds()) > DELTASEC:
                    print("ttl key expire")
                    del cache[key]

    manager = Manager()
    c = manager.dict()
    s = MyStore(c)

    worker1 = Process(target=flow, args=(s,))
    worker2 = Process(target=cleaning, args=(c,))

    worker2.daemon = True

    worker1.start()
    worker2.start()

    worker1.join()

if __name__ == "__main__":
    main()