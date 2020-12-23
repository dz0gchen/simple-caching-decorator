from typing import Union


def cache(f, limit=6, cache={}):
    def decorate(self, key, value=None):
        if f.__name__ == "set":
            # cache должен быть быстрее bakend-storage;
            # в качестве bakend-storage и cache используем словарь;
            # ограничиваем емкость cache 6 элементами, для словаря первоначально выделяется bucket на 8
            # элементов, при заполнении на 2/3 (6 элементов) идет перестройка словаря и копирование всех элементов
            # в bucket большей емкости, несмотря на оптимизацию в python > 3.6, отказываемся от этой операции
            # для повышения быстродействия cache и платим за это ограничением размера cache
            if len(cache) == limit:
                cache.clear()
                print("clear cache")
            cache[key] = value
            print("load into cache")
            return f(self, key, value)
        else:
            val = cache.get(key)
            if val is not None:
                print("return from cache")
                return val
        return f(self, key)
    return decorate


class MyStore(dict):
    """
    Эмуляция key-value storage на основе словаря.
    """
    @cache
    def set(self, key: Union[int, str], value: Union[int, str]):
        print("set data to store")
        return dict.__setitem__(self, key, value)

    @cache
    def get(self, key: Union[int, str]):
        print("cache is not used")
        return dict.__getitem__(self, key)

    def __getattribute__(self, attr):
        """
        Убираем лишние методы из словаря, согласно спецификации storage
        может иметь только set/get методы.
        """
        if attr in MyStore.__dict__ or \
                dict.__dict__[attr].__name__ in ["__getitem__", "__setitem__"]:
            return super(dict, self).__getattribute__(attr)
        else:
            raise AttributeError

def main():
    s = MyStore()

    s.set(3, 4)
    s.set("ddd", 56)
    s.set(31, 43)
    s.set("", 4)
    s.set(5, 6)
    s.set(7, 8)
    s.set(11, 12)

    s.get(3)
    s.get("ddd")
    s.get(31)
    s.get(11)

    try:
        s.get(100)
    except KeyError:
        try:
            s.pop()
        except AttributeError:
            pass

if __name__ == "__main__":
    main()