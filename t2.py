import os

dirs = list(filter(lambda x: os.path.isdir(x), os.listdir(os.path.dirname(os.path.abspath(__file__)))))
print(dirs)
