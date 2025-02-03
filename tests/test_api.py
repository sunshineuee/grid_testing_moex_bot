from tinkoff.invest import Client

TOKEN = "t.MVpsPB9gQlrxx-NAMIpd6udOJg9tLlDWoSDbIG5M7lXfgxXLpEzxGQssnzelVnnN9jaYbUMPV1XJr_zKUW8P7g"

with Client(TOKEN) as client:
    accounts = client.users.get_accounts()
    print(accounts)
