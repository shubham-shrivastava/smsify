import re

regex = re.compile(r'\+91')
str0 = "+918236028730"
str1 = "+918236028730"
str3 = "8236028730"

print(bool(regex.search(str0)))
print(bool(regex.search(str1)))
print(bool(regex.search(str3)))
