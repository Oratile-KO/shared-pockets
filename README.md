# shared-pockets

A Python application for managing flexible stokvel contributions, loans, repayments, and year-end member settlements.

## About

This project is being developed as a practical Python learning project based on a real-world family stokvel.

The stokvel allows members to contribute flexible amounts without a fixed monthly contribution requirement. Members can contribute different amounts and may skip contributions.

The group allows both members and external borrowers to borrow money from the collective pool.

The project focuses on building a practical financial management system while learning Python, SQLite, database design, and software development practices.

## Current Features

* Member management
* Flexible contribution tracking
* Member and group contribution totals
* SQLite database persistence
* Member loans
* External borrower management
* Loan tracking
* Loan repayments
* FIFO loan repayment allocation
* Loan status tracking
* Repayment history
* Repayment allocation history
* Settlement preview
* Year-end settlement business rules

## Settlement Model

Shared Pockets separates the theoretical value of the stokvel from the money currently available in the pool.

### Theoretical Pool

The theoretical pool represents the total amount contributed by members.

Theoretical Pool = Total Contributions


### Currently Available Pool

The currently available pool represents contribution money that is currently available after accounting for loans and repayments.

Available Pool = Total Contributions
                  - Total Loans
                  + Total Repayments

Expenses and other withdrawals may be incorporated into this calculation in the future.

### Member Theoretical Entitlement

A member's theoretical entitlement is based on their contributions and outstanding member loans.

Outstanding Member Loan =
    Total Member Loans
    - Repayments Allocated to Member Loans

Theoretical Member Entitlement =
    Member Contributions
    - Outstanding Member Loan


A member cannot receive a negative settlement. If their outstanding loan is greater than their contribution entitlement, their settlement is R0 and the remaining amount remains an outstanding debt.

### Year-End Distribution

At year-end, the available pool is compared with the total theoretical member entitlements.

If enough money is available, members can receive their full theoretical entitlements.

If there is a shortfall, the group may choose between:

* Manual distribution based on an agreement between members
* Deferred distribution until additional money is recovered
* Proportional distribution based on each member's theoretical entitlement

The application is designed to record and support these decisions rather than automatically deciding how the family should distribute a shortfall.

## Business Rules

* Contributions are flexible; there is no fixed monthly contribution requirement.
* Members may skip contributions.
* A member's entitlement begins from their joining date.
* Member loans can reduce their year-end entitlement if they remain unpaid.
* External borrower loans do not directly reduce member entitlements, but unpaid external loans reduce the currently available pool.
* Loan repayments are allocated using FIFO (oldest outstanding loan first).
* Historical loans and repayment records are retained for auditability.
* External borrowers can have multiple loans.
* A borrower who later becomes a member retains their historical external borrower records.
* A member or external borrower can have outstanding debt after year-end.
* Settlement and distribution decisions should remain traceable to the underlying financial records.

## Planned Features

* Year-end settlement recording
* Settlement debt tracking
* Financial reports
* Data visualization
* Automated testing
* Flask web interface
* Authentication
* Deployment

## Project Status

Active development

Current development focus:

* Year-end settlement and distribution design
* Formalizing business rules before implementation

## Technologies

Currently:

* Python
* SQLite
* SQL

Planned:

* Flask
* HTML/CSS
* Pandas
* Matplotlib
* PostgreSQL
