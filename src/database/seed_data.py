"""
Seed script — inserts sample products, inventory records, and transactions.
Assumes users already exist in boarder.users (IDs 1-6).

Usage:
    python -m src.database.seed_data
"""
from sqlalchemy import text
from src.database.connection import engine


def seed():
    with engine.connect() as conn:

        print("Seeding products...")
        conn.execute(text("""
            INSERT INTO boarder.products
                (name, sku, description, price, category, unit_of_measure, is_active, owner_id, created_at, updated_at)
            VALUES
                ('Office Chair',       'CHAIR-001', 'Ergonomic office chair',          250.00, 'Furniture',    'pcs', 1, 1, GETUTCDATE(), GETUTCDATE()),
                ('Standing Desk',      'DESK-001',  'Height adjustable standing desk', 450.00, 'Furniture',    'pcs', 1, 1, GETUTCDATE(), GETUTCDATE()),
                ('Laptop Stand',       'STAND-001', 'Aluminium foldable laptop stand',  45.00, 'Accessories',  'pcs', 1, 2, GETUTCDATE(), GETUTCDATE()),
                ('Wireless Mouse',     'MOUSE-001', 'Bluetooth wireless mouse',         35.00, 'Electronics',  'pcs', 1, 2, GETUTCDATE(), GETUTCDATE()),
                ('Mechanical Keyboard','KEYB-001',  'RGB mechanical keyboard',          95.00, 'Electronics',  'pcs', 1, 3, GETUTCDATE(), GETUTCDATE()),
                ('USB-C Hub',          'HUB-001',   '7-in-1 USB-C hub',                55.00, 'Electronics',  'pcs', 1, 3, GETUTCDATE(), GETUTCDATE()),
                ('Monitor 27 inch',    'MON-001',   '4K 27-inch IPS monitor',         380.00, 'Electronics',  'pcs', 1, 1, GETUTCDATE(), GETUTCDATE()),
                ('Printer Paper A4',   'PAPER-001', 'A4 80gsm printer paper',          12.00, 'Stationery',   'box', 1, 4, GETUTCDATE(), GETUTCDATE()),
                ('Ballpoint Pens',     'PEN-001',   'Box of 50 blue ballpoint pens',    8.00, 'Stationery',   'box', 1, 4, GETUTCDATE(), GETUTCDATE()),
                ('Webcam HD',          'CAM-001',   '1080p HD webcam with mic',         75.00, 'Electronics',  'pcs', 1, 5, GETUTCDATE(), GETUTCDATE())
        """))
        print("  10 products inserted.")

        print("Seeding inventory...")
        conn.execute(text("""
            INSERT INTO boarder.inventory
                (product_id, quantity_on_hand, reorder_level, reorder_quantity, created_at, last_updated)
            VALUES
                (1,  20, 5,  15, GETUTCDATE(), GETUTCDATE()),
                (2,  10, 3,  10, GETUTCDATE(), GETUTCDATE()),
                (3,  50, 10, 30, GETUTCDATE(), GETUTCDATE()),
                (4,  75, 15, 50, GETUTCDATE(), GETUTCDATE()),
                (5,  30, 8,  20, GETUTCDATE(), GETUTCDATE()),
                (6,  40, 10, 25, GETUTCDATE(), GETUTCDATE()),
                (7,   8, 3,   5, GETUTCDATE(), GETUTCDATE()),
                (8, 200, 50, 100, GETUTCDATE(), GETUTCDATE()),
                (9, 150, 40, 80, GETUTCDATE(), GETUTCDATE()),
                (10, 25, 8,  20, GETUTCDATE(), GETUTCDATE())
        """))
        print("  10 inventory records inserted.")

        print("Seeding transactions...")
        conn.execute(text("""
            INSERT INTO boarder.transactions
                (product_id, user_id, transaction_type, quantity, unit_price, total_amount, reference_number, notes, created_at)
            VALUES
                -- Initial stock IN for all products
                (1,  1, 'IN',  20, 250.00, 5000.00, 'PO-001', 'Initial stock',        GETUTCDATE()),
                (2,  1, 'IN',  10, 450.00, 4500.00, 'PO-001', 'Initial stock',        GETUTCDATE()),
                (3,  2, 'IN',  50,  45.00, 2250.00, 'PO-002', 'Initial stock',        GETUTCDATE()),
                (4,  2, 'IN',  75,  35.00, 2625.00, 'PO-002', 'Initial stock',        GETUTCDATE()),
                (5,  3, 'IN',  30,  95.00, 2850.00, 'PO-003', 'Initial stock',        GETUTCDATE()),
                (6,  3, 'IN',  40,  55.00, 2200.00, 'PO-003', 'Initial stock',        GETUTCDATE()),
                (7,  1, 'IN',   8, 380.00, 3040.00, 'PO-004', 'Initial stock',        GETUTCDATE()),
                (8,  4, 'IN', 200,  12.00, 2400.00, 'PO-005', 'Initial stock',        GETUTCDATE()),
                (9,  4, 'IN', 150,   8.00, 1200.00, 'PO-005', 'Initial stock',        GETUTCDATE()),
                (10, 5, 'IN',  25,  75.00, 1875.00, 'PO-006', 'Initial stock',        GETUTCDATE()),
                -- Some OUT transactions (sales)
                (1,  2, 'OUT',  3, 250.00,  750.00, 'SO-001', 'Sold to client A',     GETUTCDATE()),
                (3,  3, 'OUT',  5,  45.00,  225.00, 'SO-002', 'Sold to client B',     GETUTCDATE()),
                (4,  2, 'OUT', 10,  35.00,  350.00, 'SO-003', 'Sold to client C',     GETUTCDATE()),
                (8,  4, 'OUT', 20,  12.00,  240.00, 'SO-004', 'Office supplies used', GETUTCDATE()),
                (9,  4, 'OUT', 15,   8.00,  120.00, 'SO-004', 'Office supplies used', GETUTCDATE()),
                -- A RETURN
                (4,  2, 'RETURN', 2, 35.00, 70.00,  'RT-001', 'Client C returned 2',  GETUTCDATE()),
                -- An ADJUSTMENT by admin
                (7,  1, 'ADJUSTMENT', 8, 380.00, 3040.00, 'ADJ-001', 'Stock count verified', GETUTCDATE())
        """))
        print("  17 transactions inserted.")

        conn.commit()
        print("\nAll seed data inserted successfully.")


if __name__ == "__main__":
    seed()
