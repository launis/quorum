import json

def run():
    with open('c:/src/quorum/data/db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        execs = data.get('executions', {})
        print(f"Total executions in db: {len(execs)}")
        for i, (key, ex) in enumerate(list(execs.items())[-2:]):
            print(f"Execution {i}:")
            cost = ex.get('cost_estimate')
            print(f"  cost_estimate: {cost}")
            models_used = ex.get('models_used')
            print(f"  models_used: {models_used}")
            # check usage aggregates
            
        aggregates = data.get('usage_aggregates', {})
        print(f"Total usage aggregates: {len(aggregates)}")
        for key, agg in list(aggregates.items())[-2:]:
            print(f"Aggr: {agg}")
            
if __name__ == "__main__":
    run()
