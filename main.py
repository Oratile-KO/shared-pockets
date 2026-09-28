from datetime import datetime
import sqlite3
    
def add_member(conn):
    prefix  = 'M'
    name = input("Enter member name: ").strip().capitalize()
    if not name:
        print("Name cannot be empty!")
        return
    #Generate ID
    cursor = conn.execute("""
        SELECT MAX(CAST(SUBSTR(member_id, 2) AS INTEGER))
        FROM members
    """)
    result = cursor.fetchone()
    if result[0] is None:
        max_number = 0
    else:
        max_number = result[0]
    member_id = prefix  + f"{max_number + 1:03}"
    date_joined = input("Enter date joined (YYYY-MM-DD): ")
    try:
        datetime.strptime(date_joined, "%Y-%m-%d")
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD.")
        return

    conn.execute("""
        INSERT INTO members (member_id, name, date_joined)
        VALUES (?, ?, ?)
    """, (member_id, name, date_joined))

    conn.commit()
    print("Member successfully added!")

def view_members(conn):
    cursor = conn.execute("SELECT * FROM members")
    print(f"{'ID':<7}{'Member ID':<13}{'Name':<15}")
    for row in cursor:
        id = row[0]
        member_id = row[1]
        name = row[2]
        print(f"{id:<7}{member_id:<13}{name:<15}")

def add_contribution(conn):
    member_db_id = input("Enter Member ID of the member contributing: ").strip().capitalize()
    if not member_db_id:
        print("Member ID cannot be empty! Please try again.")
        return
    cursor = conn.execute(
        "SELECT id FROM members WHERE member_id = ?",
        (member_db_id,)
    )
    result = cursor.fetchone()
    if result is None:
        print("Member ID not found! Please try again.")
        return
    member_id = result[0]
    try:
        amount = float(input(f"Enter amount member is contributing: ").strip()) 
        if amount <= 0:
                print("Enter amount greater that 0")
                return
    except ValueError:
            print("Please enter a valid amount!")
            return

    conn.execute("""
        INSERT INTO contributions (member_id, amount, date)
        VALUES (?, ?, ?)
        """, (member_id, amount, datetime.now().strftime("%Y-%m-%d")))

    conn.commit()
    print("Contribution added successfully!")

def view_contributions(conn):
    cursor = conn.execute("""
            SELECT members.member_id, members.name, contributions.amount, contributions.date
            FROM members
            INNER JOIN contributions
                ON members.id = contributions.member_id;
                    """)
    print(f"{'Member ID':<12}{'Name':<15}{'Amount':<13}{'Date':<12}")
    for row in cursor:
        member_id = row[0]
        name = row[1]
        amount = row[2]
        date = row[3]
        print(f"{member_id:<12}{name:<15}R{amount:<12,.2f}{date:<12}")

def calc_member_total(conn):
    member_id = input("Enter Member ID: ").strip().capitalize()
    if not member_id:
        print("Member ID cannot be empty! Please try again.")
        return
    cursor = conn.execute("""
                SELECT members.member_id, members.name, SUM(contributions.amount) as member_total 
                FROM members
                LEFT JOIN contributions
	                ON members.id = contributions.member_id
                WHERE members.member_id = ?
                GROUP BY members.id
                        """, (member_id,))
    result = cursor.fetchone()
    if result is None:
        print(f"Member '{member_id}' does not exist!")

    elif result[2] is None:
        print(f"{result[1]} has not made any contributions yet.")

    else:
        print(f"The total for {result[1]} is R{result[2]:,.2f}")

def calc_group_total(conn):
    cursor = conn.execute("SELECT SUM(amount) FROM contributions")
    result = cursor.fetchone()
    if result[0] is None:
        print("No contributions have been made yet.")
        return
    else:
        print(f"The total group contribution is R{result[0]:,.2f}")

def print_separator():
    print("-" * 35)

def has_members(conn):
    cursor = conn.execute("""
        SELECT EXISTS (
            SELECT 1 FROM members
        )
    """)
    return cursor.fetchone()[0]

def add_loan(conn):
    while True:
        try:
            borrower_choice = int(input("Please select borrower type: \n1. Member \n2. External\n").strip())
            if borrower_choice == 1:
                borrower_type = 'member'
                break
            elif borrower_choice == 2:
                borrower_type = 'external'
                break
            else:
                print("invalid selection, please enter '1' or '2'!")
        except ValueError:
            print("Invalid input, please enter '1' or '2'!")

    if borrower_type == 'member':
        view_members(conn)
        while True: 
            try:
                member_db_id  = int(input("Enter ID of member taking a loan: ").strip())

                cursor = conn.execute("""
                        SELECT id, member_id, name
                        FROM members
                        WHERE id = ?
                    """, (member_db_id,))
                member = cursor.fetchone()
                if member is None:
                    print(f"Member ID '{member_db_id}' does not exist, please try again!")
                else:
                    while True:
                        try:
                            amount = float(input(f"Enter amount {member[2]} wants to borrow: "))
                            if amount <= 0:
                                print("Amount cannot be below R1, please try again!")
                            else:
                                prefix = 'L'
                                cursor = conn.execute("""
                                        SELECT MAX(CAST(SUBSTR(loan_id, 2) AS INTEGER))
                                        FROM loans
                                    """)
                                result = cursor.fetchone()
                                if result[0] is None:
                                    max_number = 0
                                else:
                                    max_number = result[0]
                                loan_id = prefix  + f"{max_number + 1:03}"
                                print(loan_id)
                                date_issued = datetime.now().strftime("%Y-%m-%d")
                                conn.execute("""
                                                INSERT INTO loans(member_id, borrower_type, amount, loan_id, date_issued, status)
                                                VALUES(?, ?, ?, ?, ?, 'open')
                                            """, (member[0], borrower_type, amount, loan_id, date_issued))
                                conn.commit()
                                result = conn.execute("SELECT * FROM loans")
                                for row in result:
                                    print(row)
                                break
                        except ValueError:
                            print("Invalid input, please try again!")
                    break
            except ValueError:
                print("Invalid input, please try again!")

    if borrower_type == 'external':
       while True:
        try:
            external_type = int(input("Is the external borrower new or existing? \n1. New \n2. Existing\n").strip())
            if external_type == 1:
                while True:
                    name = input("Enter borrower name: ").strip().capitalize()
                    if not name:
                        print("Borrower name cannot be blank!")
                        continue
                    else:
                        while True:
                            try:
                                amount = float(input(f"Enter amount {name} is requesting to borrow: ").strip())
                                if amount <= 0:
                                    print("Amount cannot be below R1, please try again!")
                                else:
                                    cursor = conn.execute("""
                                                INSERT INTO borrowers(name)
                                                VALUES(?)
                                            """, (name,))
                                    borrower_db_id = cursor.lastrowid

                                    #Generate Loan ID
                                    prefix  = 'L'
                                    cursor = conn.execute("""
                                        SELECT MAX(CAST(SUBSTR(loan_id, 2) AS INTEGER))
                                        FROM loans
                                    """)
                                    result = cursor.fetchone()
                                    if result[0] is None:
                                        max_number = 0
                                    else:
                                        max_number = result[0]
                                    loan_id = prefix  + f"{max_number + 1:03}"
                                    print(loan_id)
                                    date_issued = datetime.now().strftime("%Y-%m-%d")

                                    conn.execute("""
                                                INSERT INTO loans(borrower_id, borrower_type, amount, loan_id, date_issued, status)
                                                VALUES(?, ?, ?, ?, ?, 'open')
                                            """, (borrower_db_id, borrower_type, amount, loan_id,date_issued))
                                    conn.commit()
                                    result = conn.execute("SELECT * FROM loans")
                                    for row in result:
                                        print(row)
                                    break
                            except ValueError:
                                print("Invalid amount! Please try again.")
                    break
            elif external_type == 2:
                cursor = conn.execute("""
                            SELECT * 
                            FROM borrowers
                        """)
                has_borrowers = cursor.fetchall()
                if not has_borrowers:
                    print("There are no existing external borrowers yet! Please try again.")
                    continue
                else:
                    print(f"{'ID':<5}{'Name':<15}")
                    for borrower in has_borrowers:
                        print(f"{borrower[0]:<5}{borrower[1]}")
                    while True:
                        try:
                            borrower_db_id = int(input("Enter borrower ID: ").strip())
                            cursor = conn.execute("""
                                        SELECT *
                                        FROM borrowers
                                        WHERE id = ?
                                    """, (borrower_db_id,))
                            existing_borrower = cursor.fetchone()
                            if existing_borrower is None:
                                print("Incorrect ID entered, please try again!")
                                continue
                            else:
                                while True:
                                    try:
                                        amount = float(input(f"Enter amount {existing_borrower[1]} wants to borrow: "))
                                        if amount <= 0:
                                            print("Amount cannot be below R1, please try again!")
                                            continue
                                        else:
                                            #Generate Loan ID
                                            prefix  = 'L'
                                            cursor = conn.execute("""
                                                SELECT MAX(CAST(SUBSTR(loan_id, 2) AS INTEGER))
                                                FROM loans
                                            """)
                                            result = cursor.fetchone()
                                            if result[0] is None:
                                                max_number = 0
                                            else:
                                                max_number = result[0]
                                            loan_id = prefix  + f"{max_number + 1:03}"
                                            print(loan_id)
                                            date_issued = datetime.now().strftime("%Y-%m-%d")

                                            conn.execute("""
                                                        INSERT INTO loans(borrower_id, borrower_type, amount, loan_id, date_issued, status)
                                                        VALUES(?, ?, ?, ?, ?, 'open')
                                                    """, (borrower_db_id, borrower_type, amount, loan_id,date_issued))
                                            conn.commit()
                                            result = conn.execute("SELECT * FROM loans")
                                            for row in result:
                                                print(row)
                                            break
                                    except ValueError:
                                        print("Invalid amount, please try again!")
                                break
                        except ValueError:
                            print("invalid input, please try again!")   
        except ValueError:
            print("Invalid selection, please enter either '1' or '2'!")
            continue
        break       
#create sqlite members table
try:
    with sqlite3.connect("shared_pockets.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY,
                member_id TEXT UNIQUE,
                name TEXT NOT NULL,
                date_joined DATE NOT NULL
            );
        """)
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS contributions (
                    id INTEGER PRIMARY KEY,
                    member_id INTEGER,
                    amount REAL NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (member_id) REFERENCES members(id)
            );
         """)
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS borrowers (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
            );
        """)
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY,
                    loan_id TEXT UNIQUE,
                    borrower_type TEXT NOT NULL,        
                    member_id INTEGER,
                    borrower_id INTEGER,
                    amount REAL NOT NULL,   
                    date_issued DATE NOT NULL,
                    status TEXT NOT NULL,
                    CHECK (
                        (borrower_type = 'member'
                            AND member_id IS NOT NULL
                            AND borrower_id IS NULL)
                        OR 
                        (borrower_type = 'external'
                            AND member_id IS NULL
                            AND borrower_id IS NOT NULL)
                    ),
                    FOREIGN KEY (member_id) REFERENCES members(id),
                    FOREIGN KEY (borrower_id) REFERENCES borrowers(id)
            );
        """)
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS repayments (
                    id INTEGER PRIMARY KEY,
                    amount REAL NOT NULL,
                    date DATE NOT NULL
            );
        """)
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS repayment_allocations (
                    id INTEGER PRIMARY KEY,
                    repayment_id INTEGER,
                    loan_id INTEGER,
                    amount REAL NOT NULL,
                    FOREIGN KEY (repayment_id) REFERENCES repayments(id),
                    FOREIGN KEY (loan_id) REFERENCES loans(id)
            );
                """)
        
        # Print members
        cursor = conn.execute("SELECT * FROM loans")
        print("LOANS:")
        for row in cursor:
            print(row)
        
        # Print members
        cursor = conn.execute("SELECT * FROM members")
        print("\nMEMBERS:")
        for row in cursor:
            print(row)

        # Print contributions
        cursor = conn.execute("SELECT * FROM contributions")
        print("\nCONTRIBUTIONS:")
        for row in cursor:
            print(row)

        # Print borrowers
        cursor = conn.execute("SELECT * FROM borrowers")
        print("\nBORROWERS:")
        for row in cursor:
            print(row)

        while True:
            #Prompt user to select option from the menu
            try:
                option = int(input(f"\nSelect an option: \n1. Add member \n2. View members \n3. Record contribution \n4. View contributions \n5. Calculate member total \n6. Calculate group total \n7. Add loan \n8. Close\n").strip())

                if option == 1:
                    add_member(conn)

                elif option == 2:
                    if has_members(conn):
                        print("Members")
                        print_separator()
                        view_members(conn)
                    else:
                        print("No member has been added yet.")

                elif option == 3:
                    if has_members(conn):
                        print("Available members:")
                        print_separator()
                        view_members(conn)
                        add_contribution(conn) 
                    else:
                        print("No member has been added yet.")

                elif option == 4:
                    if has_members(conn):
                        view_contributions(conn)
                    else:
                        print("No member has been added yet.")

                elif option == 5:
                    if has_members(conn):
                        print("Available members:")
                        print_separator()
                        view_members(conn)
                        calc_member_total(conn)
                    else:
                        print("No member has been added yet.")

                elif option == 6:
                    calc_group_total(conn)

                elif option == 7:
                    #if has_members(conn):
                        add_loan(conn)
                    #else:
                      #  print("No contributions have been made yet!")

                elif option == 8:
                    print("Goodbye!")
                    break

                else:
                    print("Invalid selection! Please try again.")
                    
            except ValueError:
                    print("Invalid selection! Please try again.")

except sqlite3.IntegrityError as e:
    if "UNIQUE constraint failed" in str(e):
        print("Member ID already exists. Please use a different member ID.")
    elif "FOREIGN KEY constraint failed" in str(e):
        print("That member does not exist.")
    else:
        print(f"Database Error: {e}")
