from main import allocate_repayment
import unittest

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

if __name__ == "__main__":
    unittest.main()