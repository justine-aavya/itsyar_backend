import inspect
import training_and_hackathon_sdk as foundry_osdk
client = foundry_osdk.get_client()

print('=== create_enrolment ===')
sig = inspect.signature(client.ontology.actions.create_enrolment)
for name in sig.parameters:
    print(f' {name}')

print('\n=== mark_complete ===')
sig2 = inspect.signature(client.ontology.actions.mark_complete)
for name in sig2.parameters:
    print(f' {name}')