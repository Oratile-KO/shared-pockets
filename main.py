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
    member_id = prefix  + f"{suffix:03}"
    new_member = {'name': name, 'member_id': member_id, 'contributions':  []}  #Add new member to list
    members.append(new_member)
    print(f"{name} added successfully! Member ID: {member_id}")

#Display the members and their member ID's
def view_member():
    for member in members:
        print(f"\n{member['member_id']} {member['name']}")

def find_member(member_id):
    for member in members:
        if member['member_id'] == member_id:
            return member
    return None
 
def record_contribution():
    today = date.today()
    view_member()   
    member_id = input("\nEnter member ID: ").strip().capitalize()
    member = find_member(member_id)
    if member:
            try: 
                amount = float(input(f"Enter amount member is contributing: ").strip()) 
                if amount <= 0:
                    print("Enter amount greater that 0")
                else:
                    new_contribution = {'amount': amount, 'date': today.strftime("%d/%b/%Y")}
                    member['contributions'].append(new_contribution)
            except ValueError: 
                print("Please enter a valid amount!")
    else:
        print(f"Member ID '{member_id}' does not exist! Please try again.")

def view_contributions():
    print("Contributions")
    print_separator()
    for member in members:
        for contribution in member['contributions']:
            print(f"\nDate \t\tMember \t\tAmount \n{contribution['date']} \t{member['name']} \t\tR{contribution['amount']:,.2f}")

def calc_member_total():
    view_member()
    member_id = input(f"Enter the member ID: ").strip().capitalize()
    member = find_member(member_id)
    total = 0
    if member:
        for contribution in member['contributions']:
            total += contribution['amount']
        if total > 0:
            print(f"Member \t\tTotal Contributed \n{member['name']} \t\tR{total:,.2f}")
        else:
            print(f"{member['name']} has not made any contributions yet!")
    else:
        print("Please enter an existing member ID")

def calc_group_total():
    group_total = 0
    for member in members:
        for contribution in member['contributions']:
            group_total += contribution['amount']
    print(f"Group total: R{group_total:,.2f}")

def has_members():
    return len(members) > 0

def print_separator():
    print("-" * 35)

while True:
    #Prompt user to select option from the menu
    try:
        option = int(input(f"\nSelect an option: \n1. Add member \n2. View members \n3. Record contribution \n4. View contributions \n5. Calculate member total \n6. Calculate group total\n").strip())

        if option == 1:
            add_member()

        elif option == 2:
            if has_members():
                print("Members")
                print_separator()
                view_member()
            else:
                print("No member has been added yet!")

        elif option == 3:
            if has_members():
                print("Available members:")
                print_separator()
                record_contribution()
            else:
                print("No member has been added yet!")

        elif option == 4:
            if has_members():
                view_contributions()
            else:
                print("No member has been added yet!")

        elif option == 5:
            if has_members():
                print("Available members:")
                print_separator()
                calc_member_total()
            else:
                print("No member has been added yet!")

        elif option == 6:
            if has_members():
             calc_group_total()
            else:
                print("No member has been added yet!")

        else:
            print("Invalid selection! Please try again.")

    except ValueError:
        print("Invalid selection! Please try again.")