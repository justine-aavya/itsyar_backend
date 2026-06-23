from training_and_hackathon_sdk.ontology.objects import VanyarUser, Courses, VanyarExercise, VanyarEnrolment , Quizes


# List ALL available filter properties
print("Available properties on VanyarUser.object_type:")
for attr in sorted(dir(VanyarUser.object_type)):
    if not attr.startswith('_'):
        print(f"  • {attr}")

print("\nAvailable properties on Courses.object_type:")
for attr in sorted(dir(Courses.object_type)):
    if not attr.startswith('_'):
        print(f"  • {attr}")


print("\nAvailable properties on VanyarExercise.object_type:")
for attr in sorted(dir(VanyarExercise.object_type)):
    if not attr.startswith('_'):
        print(f"  • {attr}")

print("\nAvailable properties on VanyarEnrolment.object_type:")
for attr in sorted(dir(VanyarEnrolment.object_type)):
    if not attr.startswith('_'):
        print(f"  • {attr}")

print("\nAvailable properties on Quizes.object_type:")
for attr in sorted(dir(Quizes.object_type)):
    if not attr.startswith('_'):
        print(f"  • {attr}")

