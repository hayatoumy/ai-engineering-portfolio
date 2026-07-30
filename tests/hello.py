# hello.py
from src.ai_engineering_portfolio.cost import tracked_create
from src.ai_engineering_portfolio.models import HAIKU

r = tracked_create(
    model=HAIKU,
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hi in five words."}],
)
print(r.content[0].text)
print(r.usage)
