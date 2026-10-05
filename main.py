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
        id = row["id"]
        member_id = row["member_id"]
        name = row["name"]
        print(f"{id:<7}{member_id:<13}{name:<15}")

def add_contribution(conn):
    while True:
        member_db_id = input("Enter Member ID of the member contributing: ").strip().capitalize()
        if not member_db_id:
            print("Member ID cannot be empty! Please try again.")
            continue
        cursor = conn.execute(
            "SELECT id FROM members WHERE member_id = ?",
            (member_db_id,)
        )
        result = cursor.fetchone()
        if result is None:
            print("Member ID not found! Please try again.")
            continue
        member_id = result[0]
        while True:
            try:
                amount = float(input(f"Enter amount member is contributing: ").strip()) 
                if amount <= 0:
                        print("Enter amount greater that 0")
                        continue
                else:
                    break
            except ValueError:
                    print("Please enter a valid amount!")

        conn.execute("""
            INSERT INTO contributions (member_id, amount, date)
            VALUES (?, ?, ?)
            """, (member_id, amount, datetime.now().strftime("%Y-%m-%d")))

        conn.commit()
        print("Contribution added successfully!")
        break 

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
    print("-" * 75)

def has_members(conn):
    cursor = conn.execute("""
        SELECT EXISTS (
            SELECT 1 FROM members
        )
    """)
    return cursor.fetchone()[0]

def add_loan(conn):
    borrower_type  = ''
    while True:
        try:
            borrower_choice = int(input("Please select borrower type: \n1. Member \n2. External Borrower \n3. Close\n").strip())

            if borrower_choice == 1:
                borrower_type = 'member'
                break

            elif borrower_choice == 2:
                borrower_type = 'external'
                break

            elif borrower_choice ==3:
                break

            else:
                print("Invalid selection, please enter '1' or '2'!")

        except ValueError:
            print("Invalid input, please enter '1' or '2'!")

    if borrower_type == 'member':
        view_members(conn)
        while True: 
                member_id  = input("Enter Member ID of member taking a loan: ").strip().capitalize()

                cursor = conn.execute("""
                        SELECT id, member_id, name
                        FROM members
                        WHERE member_id = ?
                    """, (member_id,))
                
                member = cursor.fetchone()

                if not member:
                    print(f"Member ID '{member_id}' does not exist, please try again!")

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
                                date_issued = datetime.now().strftime("%Y-%m-%d")

                                conn.execute("""
                                                INSERT INTO loans(member_id, borrower_type, amount, loan_id, date_issued, status)
                                                VALUES(?, ?, ?, ?, ?, 'open')
                                            """, (member[0], borrower_type, amount, loan_id, date_issued))
                                
                                conn.commit()
                                break

                        except ValueError:
                            print("Invalid input, please try again!")
                    break

    if borrower_type == 'external':
       while True:
        try:
            external_type = int(input("Is the external borrower new or existing? \n1. New Borrower \n2. Existing Borrower \n").strip())

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
                                    #Generate Borrower ID
                                    prefix  = 'B'
                                    cursor = conn.execute("""
                                        SELECT MAX(CAST(SUBSTR(borrower_id, 2) AS INTEGER))
                                        FROM borrowers
                                    """)
                                    result = cursor.fetchone()
                                    if result[0] is None:
                                        max_number = 0
                                    else:
                                        max_number = result[0]
                                    borrower_id = prefix  + f"{max_number + 1:03}"
                                    cursor = conn.execute("""
                                            INSERT INTO borrowers(name, borrower_id)
                                            VALUES(?, ?)
                                            """, (name, borrower_id ))
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
                                    date_issued = datetime.now().strftime("%Y-%m-%d")

                                    conn.execute("""
                                                INSERT INTO loans(borrower_id, borrower_type, amount, loan_id, date_issued, status)
                                                VALUES(?, ?, ?, ?, ?, 'open')
                                            """, (borrower_db_id, borrower_type, amount, loan_id,date_issued))
                                    conn.commit()
                                    break
                            except ValueError:
                                print("Invalid amount! Please try again.")
                    break

            elif external_type == 2:
                cursor = conn.execute("""
                            SELECT borrower_id as "borrower_id", name as "name"
                            FROM borrowers
                        """)
                has_borrowers = cursor.fetchall()

                if not has_borrowers:
                    print("There are no existing external borrowers yet! Please try again.")
                    continue

                else:
                    print(f"{'Borrower ID':<13}{'Name':<15}")

                    for borrower in has_borrowers:
                        borrower_id = borrower["borrower_id"]
                        borrower_name = borrower["name"]
                        print(f"{borrower_id:<13}{borrower_name}")

                    while True:
                            borrower_id = input("Enter borrower ID: ").strip().capitalize()

                            cursor = conn.execute("""
                                        SELECT *
                                        FROM borrowers
                                        WHERE borrower_id = ?
                                    """, (borrower_id,))
                            
                            existing_borrower = cursor.fetchone()

                            if existing_borrower is None:
                                print("Incorrect Borrower ID entered, please try again!")
                                continue

                            else:
                                while True:
                                    try:
                                        amount = float(input(f"Enter amount {borrower_name} wants to borrow: "))
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
                                            date_issued = datetime.now().strftime("%Y-%m-%d")

                                            conn.execute("""
                                                        INSERT INTO loans(borrower_id, borrower_type, amount, loan_id, date_issued, status)
                                                        VALUES(?, ?, ?, ?, ?, 'open')
                                                    """, (borrower_id, borrower_type, amount, loan_id,date_issued))
                                            conn.commit()
                                            break

                                    except ValueError:
                                        print("Invalid amount, please try again!")
                                break
        except ValueError:
            print("Invalid selection, please enter either '1' or '2'!")
            continue
        break

def view_loans(conn):
   cursor = conn.execute("""
                SELECT loans.loan_id as "Loan ID", 
                    CASE
                        WHEN loans.borrower_type = 'member' THEN members.name
                        ELSE borrowers.name
                    END AS "Borrower", 
                loans.borrower_type as "Type", loans.amount as "Amount", loans.date_issued as "Date", loans.status as "Status"
                FROM loans
                LEFT JOIN members
                    ON loans.member_id = members.id
                LEFT JOIN borrowers
                    ON loans.borrower_id = borrowers.id
                """)
   print(f"{'Loan ID':<9}{'Borrower':<15}{'Type':<12}{'Amount':<16}{'Date':<15}{'Status':<6}")
   print_separator()
   for row in cursor:
       loan_id = row["Loan ID"]
       name = row["Borrower"]
       borrower_type = row["Type"]
       amount = row["Amount"]
       date = row["Date"]
       status = row["Status"]
       print(f"{loan_id:<9}{name:<15}{borrower_type:<12}R{amount:<15,.2f}{date:<15}{status:<6}")

def update_loan_status(conn):
    conn.execute("""
                UPDATE loans
                SET status = 'closed'
                WHERE amount - COALESCE(
                (
                    SELECT SUM(repayment_allocations.amount)
                    FROM repayment_allocations
                    WHERE repayment_allocations.loan_id = loans.id
                    ),
                    0
                ) = 0;
            """)

def add_repayment(conn):
    while True:
        try:
            borrower_type = int(input("Select payment type: \n1. Member Repayment \n2. External Borrower Repayment \n3. Close\n").strip())
            if borrower_type == 1:
                cursor = conn.execute("""
                        SELECT  id as 'db_id', member_id as 'member_id', members.name as 'name'
                        FROM members
                        WHERE EXISTS (
                            SELECT 1
                            FROM loans
                            LEFT JOIN repayment_allocations
                                on loans.id = repayment_allocations.loan_id
                            WHERE loans.member_id = members.id
                            GROUP BY loans.id, loans.amount
                            HAVING loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) > 0
                            )
                    """)
                members = cursor.fetchall()
                if not members:
                    print("There are no members with outstanding loans.")
                    continue
                else:  
                    print(f"AVAILABLE MEMBERS: \n{'Member ID':<13}{'Name':<17}")
                    for row in members:
                        member_id = row['member_id']
                        name = row['name']
                        print(f"{member_id:<13}{name:<17}")
                while True:
                    member_id = input("Enter Member ID: ").strip().capitalize()
                    if not member_id:
                        print("Member ID cannot be blank!")
                        continue
                    else:
                        cursor = conn.execute("""
                                        SELECT loans.loan_id AS 'loan_id', loans.amount AS 'original', COALESCE((SUM(repayment_allocations.amount)), 0) AS 'repaid', loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) AS 'outstanding', loans.date_issued as 'date', members.id as 'db_id', members.name as 'name'
                                        FROM loans
                                        JOIN members    
                                            ON loans.member_id = members.id
                                        LEFT JOIN repayment_allocations
                                            ON loans.id = repayment_allocations.loan_id	
                                        WHERE members.member_id = ?
                                        GROUP BY loans.id, loans.loan_id, loans.amount, loans.date_issued
                                        HAVING loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) > 0
                                        ORDER BY loans.date_issued ASC, loans.id ASC    
                                            """, (member_id,))
                        member = cursor.fetchall()
                        if not member:
                            print(f"Member ID '{member_id}' has no outstanding loans, please try again!")
                            continue
                        else:
                            for id in member:
                                member_db_id = id["db_id"]
                            cursor = conn.execute("""
                                        SELECT loans.loan_id AS 'loan_id', loans.amount AS 'original', COALESCE((SUM(repayment_allocations.amount)), 0) AS 'repaid', loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) AS 'outstanding', loans.date_issued as 'date'
                                        FROM loans
                                        JOIN members
                                            ON loans.member_id = members.id
                                        LEFT JOIN repayment_allocations
                                            ON loans.id = repayment_allocations.loan_id	
                                        WHERE members.id = ?
                                        GROUP BY loans.id, loans.loan_id, loans.amount, loans.date_issued
                                        HAVING loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) > 0
                                        ORDER BY loans.date_issued ASC, loans.id ASC
                                            """, (member_db_id,))
                            print(f"{'Loan Id':<10}{'Original':<17}{'Repaid':<19}{'Outstanding':<17}{'Date':<17}")
                            print_separator()
                            member_outstanding_balance = 0
                            for member_loan in cursor:
                                loan_id = member_loan["loan_id"]
                                original_loan_amount = member_loan["original"]
                                repaid_amount = member_loan["repaid"]
                                outstanding_amount = member_loan["outstanding"]
                                member_outstanding_balance += outstanding_amount
                                date_issued = member_loan["date"]
                                print(f"{loan_id:<10}R{original_loan_amount:<17,.2F}R{repaid_amount:<17,.2F}R{outstanding_amount:<17,.2F}{date_issued:<17}")
                            while True:
                                try:
                                    for member_name in member:
                                        loan_borrower = member_name["name"]
                                    repayment_amount = float(input(f"Enter amount {loan_borrower} is repaying: ").strip())
                                    if repayment_amount < 1:
                                        print("Repayment amount cannot be below R1!, please try again!")
                                        continue
                                    elif repayment_amount > member_outstanding_balance:
                                        print(f"Repayment amount cannot be higher than R{member_outstanding_balance:,.2f}, please try again!")
                                        continue
                                    else:
                                        remaining_payment = repayment_amount
                                        allocations = []

                                        for loan in member:
                                            outstanding = loan["outstanding"]

                                            if remaining_payment >= outstanding:
                                                repaid_amount = outstanding
                                                remaining_payment -= outstanding 
                                            else:
                                                repaid_amount = remaining_payment
                                                remaining_payment -= remaining_payment

                                            recorded_allocations = (loan["loan_id"], repaid_amount)
                                            allocations.append(recorded_allocations)

                                            if  remaining_payment == 0:
                                                break
                                        
                                        #Generate Repayment ID
                                        prefix  = 'R'
                                        cursor = conn.execute("""
                                                SELECT MAX(CAST(SUBSTR(repayment_id, 2) AS INTEGER))
                                                FROM repayments
                                            """)
                                        result = cursor.fetchone()
                                        if result[0] is None:
                                            max_number = 0
                                        else:
                                            max_number = result[0]
                                        repaymend_id = prefix  + f"{max_number + 1:03}"
                                        date_paid = datetime.now().strftime("%Y-%m-%d")
                                        
                                        cursor = conn.execute("""
                                                INSERT INTO repayments(amount, repayment_id, date)
                                                VALUES(?, ?, ?)
                                            """, (repayment_amount, repaymend_id, date_paid,))

                                        repayment_db_id = cursor.lastrowid

                                        for allocation in allocations:
                                            allocation_loan_id, allocation_repaid_amount = allocation

                                            cursor = conn.execute("""
                                                SELECT id as "db_id"
                                                FROM loans
                                                WHERE loan_id = ?
                                            """, (allocation_loan_id,))

                                            loan = cursor.fetchone()
                                            loan_db_id = loan["db_id"]

                                            conn.execute("""
                                                INSERT INTO repayment_allocations(repayment_id, loan_id, amount)
                                                VALUES(?, ?, ?)
                                            """, (repayment_db_id, loan_db_id, allocation_repaid_amount))
                                        update_loan_status(conn)
                                        conn.commit()
                                        print("Repayment amount accepted!")
                                except ValueError:
                                    print("Invalid amount, please try again")
                                    continue
                                break 
                            break
                        
            elif borrower_type == 2:
                    cursor = conn.execute("""
                            SELECT  id as 'db_id', borrower_id as 'borrower_id', name as 'name'
                            FROM borrowers
                            WHERE EXISTS (
                                SELECT 1
                                FROM loans
                                LEFT JOIN repayment_allocations
                                    on loans.id = repayment_allocations.loan_id
                                WHERE loans.borrower_id = borrowers.id
                                GROUP BY loans.id, loans.amount
                                HAVING loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) > 0
                                )
                        """)
                    borrowers = cursor.fetchall()
                    if not borrowers:
                        print("There are no borrowers with outstanding loans.")
                        continue
                    else:  
                        print(f"AVAILABLE BORROWERS: \n{'borrower ID':<13}{'Name':<17}")
                        for row in borrowers:
                            borrower_id = row['borrower_id']
                            name = row['name']
                            print(f"{borrower_id:<13}{name:<17}")
                    while True:
                        borrower_id = input("Enter borrower ID: ").strip().capitalize()
                        if not borrower_id:
                            print("borrower ID cannot be blank!")
                            continue
                        else:
                            cursor = conn.execute("""
                                            SELECT loans.loan_id AS 'loan_id', loans.amount AS 'original', COALESCE((SUM(repayment_allocations.amount)), 0) AS 'repaid', loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) AS 'outstanding', loans.date_issued as 'date', borrowers.id as 'db_id', borrowers.name as 'name'
                                            FROM loans
                                            JOIN borrowers
                                                ON loans.borrower_id = borrowers.id
                                            LEFT JOIN repayment_allocations
                                                ON loans.id = repayment_allocations.loan_id	
                                            WHERE borrowers.borrower_id = ?
                                            GROUP BY loans.id, loans.loan_id, loans.amount, loans.date_issued
                                            HAVING loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) > 0
                                            ORDER BY loans.date_issued ASC, loans.id ASC    
                                                """, (borrower_id,))
                            borrower = cursor.fetchall()
                            if not borrower:
                                print(f"borrower ID '{borrower_id}' has no outstanding loans, please try again!")
                                continue
                            else:
                                for id in borrower:
                                    borrower_db_id = id["db_id"]
                                cursor = conn.execute("""
                                            SELECT loans.loan_id AS 'loan_id', loans.amount AS 'original', COALESCE((SUM(repayment_allocations.amount)), 0) AS 'repaid', loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) AS 'outstanding', loans.date_issued as 'date'
                                            FROM loans
                                            JOIN borrowers
                                                ON loans.borrower_id = borrowers.id
                                            LEFT JOIN repayment_allocations
                                                ON loans.id = repayment_allocations.loan_id	
                                            WHERE borrowers.id = ?
                                            GROUP BY loans.id, loans.loan_id, loans.amount, loans.date_issued
                                            HAVING loans.amount - COALESCE(SUM(repayment_allocations.amount), 0) > 0
                                            ORDER BY loans.date_issued ASC, loans.id ASC
                                                """, (borrower_db_id,))
                                print(f"{'Loan Id':<10}{'Original':<17}{'Repaid':<19}{'Outstanding':<17}{'Date':<17}")
                                print_separator()
                                borrower_outstanding_balance = 0
                                for borrower_loan in cursor:
                                    loan_id = borrower_loan["loan_id"]
                                    original_loan_amount = borrower_loan["original"]
                                    repaid_amount = borrower_loan["repaid"]
                                    outstanding_amount = borrower_loan["outstanding"]
                                    borrower_outstanding_balance += outstanding_amount
                                    date_issued = borrower_loan["date"]
                                    print(f"{loan_id:<10}R{original_loan_amount:<17,.2F}R{repaid_amount:<17,.2F}R{outstanding_amount:<17,.2F}{date_issued:<17}")
                                while True:
                                    try:
                                        for borrower_name in borrower:
                                            loan_borrower = borrower_name["name"]
                                        repayment_amount = float(input(f"Enter amount {loan_borrower} is repaying: ").strip())
                                        if repayment_amount < 1:
                                            print("Repayment amount cannot be below R1!, please try again!")
                                            continue
                                        elif repayment_amount > borrower_outstanding_balance:
                                            print(f"Repayment amount cannot be higher than R{borrower_outstanding_balance:,.2f}, please try again!")
                                            continue
                                        else:
                                            remaining_payment = repayment_amount
                                            allocations = []
                    
                                            for loan in borrower:
                                                outstanding = loan["outstanding"]
                    
                                                if remaining_payment >= outstanding:
                                                    repaid_amount = outstanding
                                                    remaining_payment -= outstanding 
                                                else:
                                                    repaid_amount = remaining_payment
                                                    remaining_payment -= remaining_payment
                    
                                                recorded_allocations = (loan["loan_id"], repaid_amount)
                                                allocations.append(recorded_allocations)
                    
                                                if  remaining_payment == 0:
                                                    break

                                            #Generate Repayment ID
                                            prefix  = 'R'
                                            cursor = conn.execute("""
                                                SELECT MAX(CAST(SUBSTR(loan_id, 2) AS INTEGER))
                                                FROM repayments
                                            """)
                                            result = cursor.fetchone()
                                            if result[0] is None:
                                                max_number = 0
                                            else:
                                                max_number = result[0]
                                            repaymend_id = prefix  + f"{max_number + 1:03}"
                                            date_paid = datetime.now().strftime("%Y-%m-%d")

                                            cursor = conn.execute("""
                                                INSERT INTO repayments(amount, repayment_id, date)
                                                VALUES(?, ?, ?)
                                            """, (repayment_amount, repaymend_id, date_paid,))
                    
                                            repayment_db_id = cursor.lastrowid
                    
                                            for allocation in allocations:
                                                allocation_loan_id, allocation_repaid_amount = allocation
                    
                                                cursor = conn.execute("""
                                                    SELECT id as "db_id"
                                                    FROM loans
                                                    WHERE loan_id = ?
                                                """, (allocation_loan_id,))
                    
                                                loan = cursor.fetchone()
                                                loan_db_id = loan["db_id"]
                    
                                                conn.execute("""
                                                    INSERT INTO repayment_allocations(repayment_id, loan_id, amount)
                                                    VALUES(?, ?, ?)
                                                """, (repayment_db_id, loan_db_id, allocation_repaid_amount))
                                            update_loan_status(conn)
                                            conn.commit()
                                            print("Repayment amount accepted!")
                                    except ValueError:
                                        print("Invalid amount, please try again")
                                        continue
                                    break 
                                break
            elif borrower_type == 3:
                break
            else:
                print("Invalid selection, please try again!")
                continue

        except ValueError:
            print("Invalid input, please try again!")
            continue
        break

def view_repayments(conn):
    cursor = conn.execute("""
                    SELECT repayment_id as "repayment_id", amount as "amount", date as "date"
                    FROM repayments
                """)
    repayments = cursor.fetchall()
    print(f"{'Repayment ID':<15}{'Date':<17}{'Amount'}")
    for payment in repayments:
        repayment_id = payment["repayment_id"]
        amount = payment["amount"]
        date = payment["date"]
        print(f"{repayment_id:<15}{date:<17}R{amount:<17,.2f}")

    while True:
        try:
            option = int(input("\nWould you like to see allocations for a particular repayment? \n1. Yes \n2. No \n").strip())

            if option == 1:
                while True:
                    selected_id = input("Enter the Repayment ID: ").strip().capitalize()

                    cursor = conn.execute("""
                            SELECT loans.loan_id as "loan_id", repayment_allocations.amount as "amount", repayments.repayment_id as "repayment_id", repayments.amount as "repayment_amount", repayments.date as "date"
                            FROM repayment_allocations
                            JOIN loans
                                ON repayment_allocations.loan_id = loans.id
                            JOIN repayments
                                ON repayment_allocations.repayment_id = repayments.id
                            WHERE repayments.repayment_id = ?
                    """, (selected_id,))

                    allocations = cursor.fetchall()

                    if not allocations:
                        print(f"Repayment ID '{selected_id}' does not exist, please try again!")
                        continue
                    else:
                        repayment_amount = allocations[0]["repayment_amount"]
                        date_paid = allocations[0]["date"]

                        print(f"Repayment: R{repayment_amount:<,.2f} \nDate: {date_paid} \n")

                        print(f"{'Loan ID':<10}{'Amount'}")
                        for allocation in allocations:
                            loan_id = allocation["loan_id"]
                            amount = allocation["amount"]
                            print(f"{loan_id:<10}R{amount:<17,.2f}")
                    break
                break
            if option == 2:
                break
            else:
                print("Invalid selection, please try again!")
        except ValueError:
            print("Please enter either '1' or '2'!")
            continue
        break

def settlements(conn):
    cursor = conn.execute("""
                SELECT 
                    members.member_id as "member_id", 
                    members.name as "name", 
                    (
                        SELECT COALESCE(SUM(amount), 0)
                        FROM contributions
                        WHERE members.id = contributions.member_id
                    ) AS total_contributions,
                    (
                        SELECT COALESCE(SUM(amount), 0)
                        FROM loans
                        WHERE members.id = loans.member_id
                    ) as total_loans,
                    (
                        SELECT COALESCE(SUM(repayment_allocations.amount), 0)
                        FROM repayment_allocations
                        JOIN loans
                            ON loans.id = repayment_allocations.loan_id
                        WHERE members.id = loans.member_id
                    ) as total_repayments
                FROM members
        """)
    settlements = cursor.fetchall()

    print(f"{'Member ID':<15}{'Name':<17}{'Contributions':<15}{'Loans':<17}{'Repayments':<15}{'Outstanding Loan':<17}{'Settlement'}")
    print_separator()
    for settlement in settlements:
        member_id = settlement["member_id"]
        member_name = settlement["name"]
        total_contributed = settlement["total_contributions"]
        total_loaned = settlement["total_loans"]
        total_repayed = settlement["total_repayments"]
        outstanding_loan = total_loaned - total_repayed
        settlement_amount = total_contributed - outstanding_loan #Preview
        print(f"{member_id:<15}{member_name:<17}R{total_contributed:<15,.2f}R{total_loaned:<15,.2f}R{total_repayed:<15,.2f}R{outstanding_loan:<15,.2f}R{settlement_amount:,.2f}")
    

#create sqlite members table
try:
    with sqlite3.connect("shared_pockets.db") as conn:
        conn.row_factory = sqlite3.Row
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
                    borrower_id TEXT UNIQUE NOT NULL,
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
                    repayment_id TEXT UNIQUE,
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
        # conn.execute("""
        #             INSERT INTO contributions (member_id, amount, date)
        #             VALUES
        #                 ((SELECT id FROM members WHERE name = 'Kutlwano'), 200.00, '2026-01-15'),
        #                 ((SELECT id FROM members WHERE name = 'Kutlwano'), 200.00, '2026-02-15'),
        #                 ((SELECT id FROM members WHERE name = 'Kutlwano'), 200.00, '2026-03-15'),
        #                 ((SELECT id FROM members WHERE name = 'Kutlwano'), 200.00, '2026-04-15'),
        #                 ((SELECT id FROM members WHERE name = 'Kutlwano'), 200.00, '2026-05-15'),
        #                 ((SELECT id FROM members WHERE name = 'Kutlwano'), 200.00, '2026-06-15'),

        #                 ((SELECT id FROM members WHERE name = 'Mmami'), 200.00, '2026-01-15'),
        #                 ((SELECT id FROM members WHERE name = 'Mmami'), 200.00, '2026-02-15'),
        #                 ((SELECT id FROM members WHERE name = 'Mmami'), 200.00, '2026-03-15'),
        #                 ((SELECT id FROM members WHERE name = 'Mmami'), 200.00, '2026-04-15'),

        #                 ((SELECT id FROM members WHERE name = 'Omphemetse'), 500.00, '2026-04-15'),

        #                 ((SELECT id FROM members WHERE name = 'Refilwe'), 200.00, '2026-02-15'),

        #                 ((SELECT id FROM members WHERE name = 'Rorisang'), 200.00, '2026-02-15'),
        #                 ((SELECT id FROM members WHERE name = 'Rorisang'), 300.00, '2026-05-15'),

        #                 ((SELECT id FROM members WHERE name = 'Tlamelo'), 200.00, '2026-01-15'),
        #                 ((SELECT id FROM members WHERE name = 'Tlamelo'), 200.00, '2026-02-15'),

        #                 ((SELECT id FROM members WHERE name = 'Tshidiso'), 200.00, '2026-02-15'),

        #                 ((SELECT id FROM members WHERE name = 'Tumisang'), 1000.00, '2026-04-15');

        #         """)
        
        # conn.execute("""
        #             INSERT INTO borrowers (borrower_id, name)
        #             VALUES
        #                 ('B001', 'Omphile'),
        #                 ('B002', 'Dinkwetse'),
        #                 ('B003', 'Lavida');
        #     """)
       
        # conn.execute("""
        #             INSERT INTO loans (
        #                 loan_id,
        #                 borrower_type,
        #                 member_id,
        #                 borrower_id,
        #                 amount,
        #                 date_issued,
        #                 status
        #             )
        #             VALUES
        #             (
        #                     'L001',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Tshidiso'),
        #                     NULL,
        #                     400.00,
        #                     '2026-03-10',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L002',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Tshidiso'),
        #                     NULL,
        #                     100.00,
        #                     '2026-05-12',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L003',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Tshidiso'),
        #                     NULL,
        #                     500.00,
        #                     '2026-06-17',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L004',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Tumisang'),
        #                     NULL,
        #                     2000.00,
        #                     '2026-03-17',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L005',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Omphemetse'),
        #                     NULL,
        #                     100.00,
        #                     '2026-04-04',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L006',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Kutlwano'),
        #                     NULL,
        #                     300.00,
        #                     '2026-04-11',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L007',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Kutlwano'),
        #                     NULL,
        #                     2800.00,
        #                     '2026-04-11',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L008',
        #                     'external',
        #                     NULL,
        #                     (SELECT id FROM borrowers WHERE borrower_id = 'B001'),
        #                     700.00,
        #                     '2026-04-10',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L009',
        #                     'external',
        #                     NULL,
        #                     (SELECT id FROM borrowers WHERE borrower_id = 'B002'),
        #                     2200.00,
        #                     '2026-05-25',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L010',
        #                     'external',
        #                     NULL,
        #                     (SELECT id FROM borrowers WHERE borrower_id = 'B003'),
        #                     1000.00,
        #                     '2026-06-17',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L011',
        #                     'external',
        #                     NULL,
        #                     (SELECT id FROM borrowers WHERE borrower_id = 'B003'),
        #                     500.00,
        #                     '2026-07-05',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L012',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Omphemetse'),
        #                     NULL,
        #                     100.00,
        #                     '2026-08-07',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L013',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Omphemetse'),
        #                     NULL,
        #                     200.00,
        #                     '2026-08-16',
        #                     'Open'
        #                 ),
        #                 (
        #                     'L014',
        #                     'member',
        #                     (SELECT id FROM members WHERE name = 'Omphemetse'),
        #                     NULL,
        #                     100.00,
        #                     '2026-09-02',
        #                     'Open'
        #                 );

        #         """)
        # conn.execute("""
        #             INSERT INTO repayments (repayment_id, amount, date)
        #             VALUES
        #                 ('R001', 2000.00, '2026-04-02'),
        #                 ('R002', 1000.00, '2026-04-30'),
        #                 ('R003', 1100.00, '2026-05-25'),
        #                 ('R004', 200.00,  '2026-05-30'),
        #                 ('R005', 2200.00, '2026-06-17'),
        #                 ('R006', 500.00,  '2026-06-17'),
        #                 ('R007', 200.00,  '2026-06-30');

        #         """)
        # conn.execute("""
        #            INSERT INTO repayment_allocations (repayment_id, loan_id, amount)
        #             VALUES
        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R001'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L004'),
        #                 2000.00
        #             ),

        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R002'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L006'),
        #                 300.00
        #             ),
        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R002'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L007'),
        #                 700.00
        #             ),

        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R003'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L007'),
        #                 1100.00
        #             ),

        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R004'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L008'),
        #                 200.00
        #             ),

        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R005'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L009'),
        #                 2200.00
        #             ),

        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R006'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L001'),
        #                 400.00
        #             ),
        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R006'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L002'),
        #                 100.00
        #             ),
        #             (
        #                 (SELECT id FROM repayments WHERE repayment_id = 'R007'),
        #                 (SELECT id FROM loans WHERE loan_id = 'L008'),
        #                 200.00
        #             );

        #         """)

        while True:
            #Prompt user to select option from the menu
            try:
                option = int(input(f"\nSelect an option: \n1. Add member \n2. View members \n3. Record contribution \n4. View contributions \n5. Calculate member total \n6. Calculate group total \n7. Add loan \n8. View loans \n9. Add Repayment \n10. View repayment allocations \n11. Close \n").strip())

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
                    view_loans(conn)

                elif  option == 9:
                    add_repayment(conn)

                elif  option == 10:
                    view_repayments(conn)

                elif  option == 11:
                    settlements(conn)

                elif option == 12:
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