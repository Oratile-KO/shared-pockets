from main import allocate_repayment, validate_repayment, create_tables, create_repayment
from unittest.mock import patch
import unittest, sqlite3


class TestAllocateRepayment(unittest.TestCase):

    def setUp(self):
        self.loans = [
            {
                'loan_id': 'L001',
                'original': 300.0,
                'repaid': 0.0,
                'outstanding': 300.0,
                'date': '2026-01-10',
                'db_id': 1,
                'name': 'John Dube'
            },
            {
                'loan_id': 'L002',
                'original': 500.0,
                'repaid': 0.0,
                'outstanding': 500.0,
                'date': '2026-02-15',
                'db_id': 2,
                'name': 'John'
            }
        ]

    def test_partial_repayment_across_two_loans(self):
        repayment_amount = 400
        repayment_allocations = allocate_repayment(repayment_amount, self.loans)
        expected_results = [("L001", 300.0), ("L002", 100.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_repayment_does_not_reach_second_loan(self):
        #self.loans.clear()
        repayment_amount = 200
        repayment_allocations = allocate_repayment(repayment_amount, self.loans)
        expected_results = [("L001", 200.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_exact_repayment_allocates_oldest_allocation(self):
        repayment_amount = 300
        repayment_allocations = allocate_repayment(repayment_amount, self.loans)
        expected_results = [("L001", 300.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_repayment_exceeds_total_outstanding(self):
        repayment_amount = 1000
        repayment_allocations = allocate_repayment(repayment_amount, self.loans)
        expected_results = [("L001", 300.0), ("L002", 500.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_no_loans_returns_empty_allocations(self):
        repayment_amount =  400
        repayment_allocations = allocate_repayment(repayment_amount, [])
        expected_results = []

        self.assertEqual(repayment_allocations, expected_results)

    def test_repayment_allocates_across_three_loans(self):
        repayment_amount =  450
        loans = [
        {
            'loan_id': 'L001',
            'original': 100.0,
            'repaid': 0.0,
            'outstanding': 100.0,
            'date': '2026-01-10',
            'db_id': 1,
            'name': 'John'
        },
        {
            'loan_id': 'L002',
            'original':200.0,
            'repaid': 0.0,
            'outstanding': 200.0,
            'date': '2026-02-15',
            'db_id': 2,
            'name': 'John'
        },
        {
            'loan_id': 'L003',
            'original': 500.0,
            'repaid': 0.0,
            'outstanding': 500.0,
            'date': '2026-02-17',
            'db_id': 3,
            'name': 'John'
        }
        ]

        repayment_allocations = allocate_repayment(repayment_amount, loans)
        expected_results = [("L001", 100.0), ("L002", 200.0), ("L003", 150.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_allocation_follows_supplied_loan_order(self):
        repayment_amount = 150
        loans = [
            {
                'loan_id': 'L002',
                'outstanding': 200.0,
            },
            {
                'loan_id': 'L001',
                'outstanding': 100.0
            }
        ]

        repayment_allocations = allocate_repayment(repayment_amount, loans)
        expected_results = [("L002", 150)]

        self.assertEqual(repayment_allocations, expected_results)

class TestValidateRepayment(unittest.TestCase):

    def test_valid_payment_amount(self):
        with patch('builtins.input', return_value="200"):
            repayment_amount = validate_repayment("John", 500)

        self.assertEqual(repayment_amount, 200.0)

    def test_non_numeric_input_then_valid_repayment(self):
        with patch('builtins.input', side_effect=["hello", "200"]) as mock_input:
            repayment_amount = validate_repayment("John", 500)

        self.assertEqual(repayment_amount, 200.0)
        self.assertEqual(mock_input.call_count, 2)

    def test_repayment_below_minimum_then_valid_repayment(self):
        with patch('builtins.input', side_effect=["0.50", "200"]) as mock_input:
            repayment_amount = validate_repayment("John", 500)

        self.assertEqual(repayment_amount, 200.0)
        self.assertEqual(mock_input.call_count, 2)

    def test_repayment_above_outstanding_balance_then_valid_repayment(self):
        with patch('builtins.input', side_effect=["600", "400"]) as mock_input:
            repayment_amount = validate_repayment("John", 500)

        self.assertEqual(repayment_amount, 400.0)
        self.assertEqual(mock_input.call_count, 2)

    def test_repayment_equal_to_outstanding_balance(self):
        with patch('builtins.input',  return_value = "500"):
            repayment_amount = validate_repayment("John", 500)

        self.assertEqual(repayment_amount, 500.0)

    def test_repayment_equal_to_minimum_amount(self):
        with patch('builtins.input',  return_value="1"):
            repayment_amount = validate_repayment("John", 500)

        self.assertEqual(repayment_amount, 1.0)

class TestTableCreation(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_create_tables(self):
        expected_table_names = {'members', 'contributions', 'loans', 'repayments', 'repayment_allocations', 'borrowers'}
        create_tables(self.conn)
        self.cursor.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                        AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                """)

        tables = self.cursor.fetchall()

        returned_table_names = set()

        for table in tables:
            returned_table_names.add(table[0])

        self.assertEqual(returned_table_names, expected_table_names)
    
    def test_contribution_rejects_invalid_member(self):
        create_tables(self.conn)
        
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                    INSERT INTO contributions(member_id, amount, date)
                    VALUES(1, 300, '2026-01-15')
                """)
        
    def test_contribution_accepts_valid_member(self):
        create_tables(self.conn)
        self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Kano','2026-01-15')
                    """)
        
        member_db_id = self.cursor.lastrowid
        
        self.cursor.execute("""
                    INSERT INTO contributions(member_id, amount, date)
                    VALUES(?, 300, '2026-01-15')
                """, (member_db_id,))

        self.cursor.execute("""
                            SELECT *
                            FROM contributions
                     """)

        contributions = self.cursor.fetchone()

        returned_contribution = contributions['amount']
        expected_contribution = 300

        self.assertEqual(returned_contribution, expected_contribution)
        self.assertEqual(contributions['member_id'], member_db_id)
            
    def test_duplicate_member_id_rejected(self):
        create_tables(self.conn)
        
        self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Mosa','2026-01-19')
                    """)
        
        with self.assertRaises(sqlite3.IntegrityError):
            self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Lemo','2026-02-20')
                    """)

    def test_member_loan_rejects_external_borrower_id(self):
        create_tables(self.conn)

        self.cursor.execute("""
                        INSERT INTO borrowers(borrower_id, name)
                        VALUES('B001', 'Sli')
                """)

        borrower_db_id = self.cursor.lastrowid

        with self.assertRaises(sqlite3.IntegrityError) as context:
            self.cursor.execute("""
                        INSERT INTO loans(loan_id, borrower_type, borrower_id, amount, date_issued, status)
                        VALUES('L001', 'member', ?, 4500, '2026-06-18', 'open')        
                """, (borrower_db_id,))

        self.assertEqual(context.exception.sqlite_errorcode, sqlite3.SQLITE_CONSTRAINT_CHECK)

    def test_member_loan_accepts_valid_member(self):
        create_tables(self.conn)

        self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Kano','2026-03-26')
                    """)

        member_db_id = self.cursor.lastrowid

        self.cursor.execute("""
                        INSERT INTO loans(loan_id, borrower_type, member_id, amount, date_issued, status)
                        VALUES('L001', 'member', ?, 2000, '2026-08-18', 'open')        
                """, (member_db_id,))

        self.cursor.execute("""
                        SELECT *
                        FROM loans
                """)

        loans  = self.cursor.fetchone()

        expected_borrower_type = 'member'
        expected_member_id = member_db_id
        expected_borrower_id = None
        expected_loan_amount = 2000

        self.assertEqual(loans['borrower_type'], expected_borrower_type)
        self.assertEqual(loans['member_id'], expected_member_id)
        self.assertEqual(loans['borrower_id'], expected_borrower_id)
        self.assertEqual(loans['amount'], expected_loan_amount)
            
    def test_external_loan_accepts_valid_external_borrower(self):
        create_tables(self.conn)

        self.cursor.execute("""
                        INSERT INTO borrowers(borrower_id, name)
                        VALUES('B001', 'James')
                    """)

        borrower_db_id = self.cursor.lastrowid

        self.cursor.execute("""
                        INSERT INTO loans(loan_id, borrower_type, borrower_id, amount, date_issued, status)
                        VALUES('L001', 'external', ?, 1500, '2026-04-12', 'open')        
                """, (borrower_db_id,))

        self.cursor.execute("""
                        SELECT *
                        FROM loans
                """)

        loans  = self.cursor.fetchone()

        expected_borrower_type = 'external'
        expected_member_id = None
        expected_borrower_id = borrower_db_id
        expected_loan_amount = 1500

        self.assertEqual(loans['borrower_type'], expected_borrower_type)
        self.assertEqual(loans['member_id'], expected_member_id)
        self.assertEqual(loans['borrower_id'], expected_borrower_id)
        self.assertEqual(loans['amount'], expected_loan_amount)

    def  test_create_repayment_records_payment_and_allocation(self):
        create_tables(self.conn)

        self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Kano','2026-03-26')
                    """)

        member_db_id = self.cursor.lastrowid

        self.cursor.execute("""
                        INSERT INTO loans(loan_id, borrower_type, member_id, amount, date_issued, status)
                        VALUES('L001', 'member', ?, 2000, '2026-08-18', 'open')        
                """, (member_db_id,))

        member_loan_db_id = self.cursor.lastrowid

        repayment_amount = 500.0

        allocations =  [("L001", 500)]

        repayment_db_id = create_repayment(self.conn, repayment_amount, allocations)

        repayment = self.cursor.execute("""
                            SELECT id, amount
                            FROM repayments
                            WHERE id = ?      
                    """, (repayment_db_id,)).fetchone()

        repayment_allocations = self.conn.execute("""
                            SELECT repayment_id, loan_id, amount
                            FROM repayment_allocations
                            WHERE repayment_id = ?
                    """, (repayment_db_id,)).fetchone()

        self.assertIsNotNone(repayment)
        self.assertEqual(repayment['amount'], repayment_amount)
        
        self.assertIsNotNone(repayment_allocations)
        self.assertEqual(repayment_allocations['repayment_id'], repayment_db_id)
        self.assertEqual(repayment_allocations['loan_id'], member_loan_db_id)
        self.assertEqual(repayment_allocations['amount'], repayment_amount)

    def test_invalid_repayment_rollback(self):
        create_tables(self.conn)

        self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Lebo','2026-09-13')
                    """)

        member_db_id = self.cursor.lastrowid

        self.cursor.execute("""
                        INSERT INTO loans(loan_id, borrower_type, member_id, amount, date_issued, status)
                        VALUES('L001', 'member', ?, 800, '2026-08-18', 'open')        
                """, (member_db_id,))
        
        self.conn.commit()

        amount = 250
        allocations = [('L001', None)]

        with self.assertRaises(sqlite3.IntegrityError):
            create_repayment(self.conn, amount, allocations)

        repayment = self.conn.execute("""
                        SELECT COUNT(*)
                        FROM repayments
                    """).fetchone()[0]

        repayment_allocations  = self.conn.execute("""
                                    SELECT COUNT(*)
                                    FROM repayment_allocations
                                """).fetchone()[0]

        member = self.conn.execute("""
                                        SELECT name
                                        FROM members
                            """).fetchone()
        
        loan = self.conn.execute("""
                                        SELECT loan_id
                                        FROM loans
                            """).fetchone()

        expected_name = 'Lebo'
        expected_loan_id = 'L001'

        self.assertEqual(repayment, 0)
        self.assertEqual(repayment_allocations, 0)
        self.assertEqual(member['name'], expected_name)
        self.assertEqual(loan['loan_id'], expected_loan_id)

    def test_create_payment_rejects_empty_repayment_allocations(self):
        create_tables(self.conn)

        self.cursor.execute("""
                        INSERT INTO members(member_id, name, date_joined)
                        VALUES('M001', 'Mosa','2026-09-13')
                    """)

        member_db_id = self.cursor.lastrowid

        self.cursor.execute("""
                        INSERT INTO loans(loan_id, borrower_type, member_id, amount, date_issued, status)
                        VALUES('L001', 'member', ?, 800, '2026-08-18', 'open')        
                """, (member_db_id,))

        self.conn.commit()

        repayment_amount = 270
        repayment_allocations = []

        with self.assertRaises(ValueError):
            create_repayment(self.conn, repayment_amount, repayment_allocations)

        repayment_records = self.cursor.execute("""
                                SELECT COUNT(*)
                                FROM repayments
                        """).fetchone()[0]
                
        repayment_allocations_records = self.cursor.execute("""
                                                SELECT COUNT(*)
                                                FROM repayment_allocations
                                        """).fetchone()[0]

        self.assertEqual(repayment_records, 0)
        self.assertEqual(repayment_allocations_records, 0)
        
if __name__ == "__main__":
    unittest.main()