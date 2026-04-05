import asyncio
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend_v2.database.factory import get_repository
from backend_v2.settings import get_settings

async def main():
    repo = await get_repository(get_settings())
    execution = await repo.get_execution('exe_72097b1a21a64fb0b5915c1e55698536')
    if not execution:
        print('Execution not found')
        return
        
    print('\n--- Tapahtumaloki (TraceEvents) koskien sr_2fa56dc36614469a ---')
    found = False
    for evt in execution.execution_trace:
        if evt.step_name == 'sr_2fa56dc36614469a':
            found = True
            print(f'\nTapahtuma tyyppi: {evt.event_type} | Aika: {evt.timestamp}')
            content = evt.content
            print(f'Tuotettu asiasisältö (avaimet): {list(content.keys()) if isinstance(content, dict) else "Ei Dict"}')
            if isinstance(content, dict):
                for k, v in content.items():
                    val_str = str(v)
                    print(f'  -> Sisäavain "{k}": pituus {len(val_str)} merkkiä')
                    if len(val_str) > 100:
                        print(f'     Esikatselu: {val_str[:150].replace(chr(10), " ")}...')
    if not found:
        print('Ei löytynyt tapahtumia tällä steppi-id:llä!')

if __name__ == '__main__':
    asyncio.run(main())
