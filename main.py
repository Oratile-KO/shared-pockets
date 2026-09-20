from datetime import date

#Declare and Initialize the members list
members = []

#Create function to add member
def add_member():
    prefix  = 'M'
    suffix = 1
    name = input("Enter member name: ").strip().capitalize()
    #Generate ID
    suffix += len(members)
    print(suffix) #Testing purposes, remove later
    member_id = prefix  + f"{suffix:03}"
    new_member = {'name': name, 'member_id': member_id, 'contributions':  []}  #Add new member to list
    members.append(new_member)
    print(f"{name} added successfully! Member ID: {member_id}\n")

#Display the members and their member ID's
def view_member():
    for member in members:
        print(f"\n{member['member_id']} {member['name']}")

#Record member contributions
def record_contribution():
    today = date.today()
    view_member()
    member_contributing = input("Enter member ID: ").strip().capitalize()
    amount = float(input(f"Enter amount member is contributing: ").strip()) 
    for member in members:
        if member['member_id'] == member_contributing:
            new_contribution = {'amount': amount, 'date': today.strftime("%d/%b/%Y")}
            member['contributions'].append(new_contribution)
    print(members) #Testing purposes,remove later

def view_contributions():
    print("Contributions")
    j = 0   
    while j < 30:
        print("-", end='')
        j += 1
    for member in members:
        for contribution in member['contributions']:
            print(f"\nDate \t\tMember \t\tAmount \n{contribution['date']} \t{member['name']} \t\t{contribution['amount']}")

def calc_member_total():
    view_member()
    member_selected = input(f"Enter the member ID: ").strip().capitalize()
    amounts = []
    for member in members:
        if member['member_id'] == member_selected:
            for contribution in member['contributions']:
                amounts.append(contribution['amount'])
            print(f"Member \t\tTotal Contributed \n{member['name']} \t\t{sum(amounts)}")

def calc_group_total():
    group_total = []
    for member in members:
        for contribution in member['contributions']:
            group_total.append(contribution['amount'])
    print(f"Group total: {sum(group_total)}")

while True:
    #Prompt user to select option from the menu
    option = int(input(f"\nSelect an option: \n1. Add member \n2. View members \n3. Record contribution \n4. View contributions \n5. Calculate member total \n6. Calculate group total\n").strip())

    if option == 1:
        add_member()

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

    elif option == 4:
        view_contributions()

    elif option == 5:
        print("Available members:")
        i = 0
        while i < 20:
            print("-", end='')
            i += 1
        calc_member_total()

    elif  option ==  6:
        calc_group_total()