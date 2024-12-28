with open(f"Pepeland Pack v.1.11.2.txt", mode="r") as file:
    file = file.read()
    print(len(file.replace("\n", "")) / 32500)
