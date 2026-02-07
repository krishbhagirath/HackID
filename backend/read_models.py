try:
    with open("models_list.txt", "rb") as f:
        content = f.read().decode("utf-16le")
        print(content)
except Exception as e:
    print(f"Error: {e}")
