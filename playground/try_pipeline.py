import sys
from pathlib import Path

import nest_asyncio

sys.path.append(str(Path(__file__).resolve().parents[1]))

nest_asyncio.apply()
from app.ai.decide import decide

question = "I want my money back, this is ridiculous."
decision = decide(question)
print(decision.model_dump_json(indent=2))