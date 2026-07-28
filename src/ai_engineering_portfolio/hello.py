# hello.py
from cost import tracked_create
from models import HAIKU

r = tracked_create(
    model=HAIKU,
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hi in five words."}],
)
print(r.content[0].text)
print(r.usage)
