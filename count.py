with open('ans.txt', 'r') as file:
    categories = file.read().splitlines()

category_count = {}

for category in categories:
    if category in category_count:
        category_count[category] += 1
    else:
        category_count[category] = 1

print("Category\tCount")
print("-----------------------")

for category, count in category_count.items():
    print("{}\t{}".format(category, count))

    # Append a newline character
    print("\n")
