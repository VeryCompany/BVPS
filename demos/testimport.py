import os
fileDir = os.path.dirname(os.path.realpath("__file__"))
print(fileDir)
mtnnDir = os.path.join(fileDir, "..", "model","1231")

print(mtnnDir)

print(os.path.join("/", "etc", "..", "usr"))
