from ping3 import ping

if not ping('vde1.asdsssa.com',10):
    print("not connected")
else:
    print("connected")
