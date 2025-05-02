import xmlrpc.client

def main():
    server = xmlrpc.client.ServerProxy("http://localhost:8000")
    
    # Añadir algunos insultos de ejemplo
    insults = [
        "You are a fool!",
        "You are an idiot!",
        "You are a nincompoop!",
        "You are a dunderhead!"
    ]
    
    for insult in insults:
        if server.add_insult(insult):
            print(f"Added insult: {insult}")
        else:
            print(f"Insult already exists: {insult}")
    
    print("\nCurrent insults:", server.get_insults())
    print("\nRandom insult:", server.get_random_insult())

if __name__ == "__main__":
    main()