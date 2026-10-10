from main import allocate_repayment
import unittest

amount = 400
second_amount = 200
third_amount = 300
fourth_amount = 1000
fifth_amount =  400

loans = [
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

class TestAllocateRepayment(unittest.TestCase):

    def test_partial_repayment_across_two_loans(self):
        repayment_allocations = allocate_repayment(amount, loans)
        expected_results = [("L001", 300.0), ("L002", 100.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_repayment_does_not_reach_second_loan(self):
        repayment_allocations = allocate_repayment(second_amount, loans)
        expected_results = [("L001", 200.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_exact_repayment_closes_oldest_allocation(self):
        repayment_allocations = allocate_repayment(third_amount, loans)
        expected_results = [("L001", 300.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_repayment_exceeds_total_outstanding(self):
        repayment_allocations = allocate_repayment(fourth_amount, loans)
        expected_results = [("L001", 300.0), ("L002", 500.0)]

        self.assertEqual(repayment_allocations, expected_results)

    def test_no_loans_returns_empty_allocations(self):
        repayment_allocations = allocate_repayment(fifth_amount, [])
        expected_results = []

        self.assertEqual(repayment_allocations, expected_results)

if __name__ == "__main__":
    unittest.main()