import Pyro4
d
def main():
    ns = Pyro4.locateNS()
    uri = ns.lookup("insult.service")
    service = Pyro4.Proxy(uri)

    insults = [
        "You are a fool!",
        "You are an idiot!",
        "You are a nincompoop!",
        "You are a dunderhead!"
    ]

    for insult in insults:
        if service.add_insult(insult):
            print(f"Added insult: {insult}")
        else:
            print(f"Insult already exists: {insult}")

    print("\nCurrent insults:", service.get_insults())
    print("\nRandom insult:", service.get_random_insult())

if __name__ == "__main__":
    main()