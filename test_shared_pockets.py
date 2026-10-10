from main import allocate_repayment, validate_repayment
from unittest.mock import patch, Mock
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

class TestCreateRepayment(unittest.TestCase):
        

if __name__ == "__main__":
    unittest.main()