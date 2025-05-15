import os,  sys
from datetime import datetime

print("hello world!")
print("当前路径：" + os.getcwd())

aa='fhfgh'
n=6.345
m=100
time=datetime.now()
print(time)

action='卖出'
print(f"=={m}--{time.strftime("%Y-%m-%d")}--{aa} \'{n:.2f}\', =={'in' if action=="买入" else 'out'}==")