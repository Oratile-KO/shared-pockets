#Declare and Initialize the members list
members = []
contributions = []
prefix  = 'M'
suffix = 1

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

while True:
    #Prompt user to select option from the menu
    option = int(input(f"\nSelect an option: \n1. Add member \n2. View members \n3. Record contribution \n4. View contributions \n5. Calculate member total \n6. Calculate group total\n").strip())
