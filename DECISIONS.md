### Decision: Introduce DraftLoan Dataclass for Deferred Execution
Date: 04 November 2026
Status: Implemented

### Context
Previously, the add_loan flow immediately executed database operations (inserting a new external borrower and issuing the loan) as soon as the user entered the amount. This created two problems:

Lack of Atomicity: If the database failed after inserting the new borrower but before inserting the loan, it left an orphaned borrower record.

Poor User Experience: The user had no opportunity to review the loan details (borrower name, amount) before the transaction was committed.

### Decision
I introduced a @dataclass DraftLoan to store the pending loan details in memory.

I refactored the loan creation paths (existing_borrower_path and external_borrower_path) to stop executing database inserts. Instead, they now return a DraftLoan object. The main flow (add_loan_rough_draft) presents this draft to the user for confirmation (or editing) before any database writes occur.

### Consequences
Positive: The gathering of data is now fully separated from the persistence layer. I can now confirm the loan details with the user before opening a database transaction.

Positive: This sets up the perfect architecture for atomicity. Once confirmed, I can pass the DraftLoan into a single service function that handles the database inserts (borrower and loan) inside one try/except/rollback block.

Positive: It decouples the CLI from the database. The dataclass is a pure data transfer object (DTO) that can eventually be passed to a web interface (Flask) instead of a CLI.

Negative / Incomplete: The current draft flow does not yet handle the "Change amount" or "Change borrower" options from the confirmation menu. (These will be implemented in a future refactor).