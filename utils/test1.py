import re

a = 'd405358-95ab-43bc-8476-3b1a6bc60bb3d405358-95ab-43bc-8476-3b1a6bc60bb3'
if re.findall("[f-z]", a):
    print("true")
else:
    print("false")
