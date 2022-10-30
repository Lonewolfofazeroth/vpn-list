from ping3 import ping

if not ping('5.183.176.92',2):
    print("not connected")
else:
    print("connected")
