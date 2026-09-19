from datetime import date

#Declare and Initialize the members list
members = []
contributions = []
prefix  = 'M'
suffix = 1
today = date.today()

#Create function to add member
def add_member(prefix, suffix):
    name = input("Enter member name: ").strip().capitalize()
    #Generate ID
    suffix += len(members)
    print(suffix) #Testing purposes, remove later
    member_id = prefix  + f"{suffix:03}"
    new_member = {'name': name, 'member_id': member_id}  #Add new member to list
    members.append(new_member)
    print(f"{name} added successfully! Member ID: {member_id}\n")

#Display the members and their member ID's
def view_member():
    for member in members:
        print(f"\n{member['member_id']} {member['name']}")

#Record member contributions
def record_contribution():
    view_member()
    member_contributing = input("Enter member ID: ").strip().capitalize()
    amount = float(input(f"Enter amount member is contributing: ").strip()) 
    for contribution in members:
        if contribution['member_id'] == member_contributing:
            new_contribution = {'name':contribution['name'], 'member_id': member_contributing, 'amount': amount, 'date': today.strftime("%d/%b/%Y")}
            contributions.append(new_contribution)
    print(contributions) #Testing purposes,remove later

while True:
    #Prompt user to select option from the menu
    option = int(input(f"\nSelect an option: \n1. Add member \n2. View members \n3. Record contribution \n4. View contributions \n5. Calculate member total \n6. Calculate group total\n").strip())

    if option == 1:
        add_member(prefix, suffix)

    elif option == 2:
        print("Members")
        i = 0
        while i < 20:
            print("-", end='')
            i += 1
        view_member()

    elif option == 3:
        print("Available members:")
        i = 0
        while i < 20:
            print("-", end='')
            i += 1
        record_contribution()