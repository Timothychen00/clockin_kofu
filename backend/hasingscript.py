import hashlib
data1=hashlib.md5()
data1.update(b"1")
print(data1.hexdigest())
print("c4ca4238a0b923820dcc509a6f75849b")