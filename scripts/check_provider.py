"""One live synthetic-evidence check. Never prints credentials or provider payloads."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from eduapp.generation import generate, ProviderError

try:
    result=generate('কল্যাণীর বয়স কত?', 'bn', [
        {'id':'synthetic-check','page':1,'text':'কল্যাণীর বয়স পনেরো বছর।'}
    ], [])
    if result['status'] != 'answered' or not result['citations']:
        raise ValueError('Provider did not produce a supported answer')
    print('PASS: live Gemini response passed schema and exact citation validation')
except (ProviderError, ValueError) as exc:
    print('FAIL:', exc.message if isinstance(exc,ProviderError) else str(exc))
    raise SystemExit(1)
