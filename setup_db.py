import sqlite3

# 1. Database Connection (Creates factory.db file)
conn = sqlite3.connect('factory.db')
cursor = conn.cursor()

# 2. Employees Table Create Karein
cursor.execute('''
CREATE TABLE IF NOT EXISTS employees (
    emp_code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    total_leaves INT DEFAULT 12
)
''')

# 3. Leave Applications Table Create Karein
cursor.execute('''
CREATE TABLE IF NOT EXISTS leave_applications (
    app_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_code TEXT,
    leave_type TEXT,
    start_date TEXT,
    end_date TEXT,
    total_days INT,
    reason TEXT,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (emp_code) REFERENCES employees(emp_code)
)
''')

# 4. Image Ka Saara Data Insert Karein
employees_data = [
    # Labour
    ('L001', 'TULSHI BARMAN', 'Labour'),
    ('L002', 'BABY THAKUR', 'Labour'),
    ('L003', 'NANIBALA SIL', 'Labour'),
    ('L004', 'PUNAM MUNDA', 'Labour'),
    ('L005', 'NEHA CHOUDHARY', 'Labour'),
    ('L006', 'SUSHILA ROY', 'Labour'),
    ('L007', 'SABITA DAS', 'Labour'),
    ('L008', 'RAKESH BARMAN', 'Labour'),
    ('L009', 'BARUN MANDAL', 'Labour'),
    ('L010', 'AKIMUL ISLAM', 'Labour'),
    ('L011', 'RIPAN DAS', 'Labour'),
    ('L012', 'HARI SHANKAR', 'Labour'),
    ('L013', 'RAJIB BARMAN', 'Labour'),
    ('L014', 'SUDAN BARMAN', 'Labour'),
    # Operator
    ('O001', 'MAHESH DAS', 'Operator'),
    ('O002', 'SATADAL DAS', 'Operator'),
    ('O003', 'JAGANATH BARMAN', 'Operator'),
    # Field Supervisor
    ('FS001', 'Subham Kariwal', 'Field Supervisor'),
    ('FS002', 'Paritosh Sil', 'Field Supervisor'),
    ('FS003', 'Ram Narayan Gupta', 'Field Supervisor'),
    # Office Executive
    ('OE001', 'Parasuram Jha', 'Office Executive'),
    ('OE002', 'Binod Kumar Mishra', 'Office Executive'),
    ('OE003', 'Pabitra Das', 'Office Executive')
]

cursor.executemany('INSERT OR IGNORE INTO employees (emp_code, name, department) VALUES (?, ?, ?)', employees_data)
conn.commit()
conn.close()

print("✅ Database aur Employees ka Data Safaltapoorvak Setup Ho Gaya!")