import requests

print("port:", end=' ')
port = int(input())

while(True):
    line = input()
    ans = requests.post(f"http://localhost:{port}", json={'type': 'Q', 'input': line})
    print(ans.text)

