# Smart Community Platform Database Design Documentation

## Database Overview
This project uses SQLite database, located at `instance/community.db`

## Database Table Structure

### 1. residents
```sql
CREATE TABLE residents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- Resident name
    age INTEGER NOT NULL,                  -- Age
    apartment_number TEXT NOT NULL,        -- Apartment number
    phone_number TEXT NOT NULL,            -- Phone number
    password TEXT NOT NULL,                -- Password (encrypted)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation time
);
```

### 2. utility_bills
```sql
CREATE TABLE utility_bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment_number TEXT NOT NULL,        -- Apartment number
    bill_type TEXT NOT NULL,              -- Bill type (water/electricity)
    amount DECIMAL(10,2) NOT NULL,        -- Amount
    status TEXT DEFAULT 'Unpaid',         -- Payment status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Creation time
    paid_at TIMESTAMP                     -- Payment time
);
```

### 3. visitors
```sql
CREATE TABLE visitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_name TEXT NOT NULL,           -- Visitor name
    id_number TEXT NOT NULL,              -- ID card number
    phone TEXT NOT NULL,                  -- Contact number
    visit_apartment TEXT NOT NULL,        -- Apartment to visit
    purpose TEXT NOT NULL,                -- Purpose of visit
    visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Visit time
    leave_time TIMESTAMP,                -- Departure time
    status TEXT DEFAULT 'Visiting',       -- Visitor status
    FOREIGN KEY (visit_apartment) REFERENCES residents(apartment_number)
);
```

### 4. maintenance
```sql
CREATE TABLE maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    apartment_number TEXT NOT NULL,        -- Reporting apartment
    type TEXT NOT NULL,                    -- Maintenance type
    description TEXT NOT NULL,             -- Problem description
    location TEXT NOT NULL,                -- Specific location
    status TEXT DEFAULT 'Pending',         -- Processing status
    submit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Submission time
    complete_time TIMESTAMP,               -- Completion time
    FOREIGN KEY (apartment_number) REFERENCES residents(apartment_number)
);
```

### 5. notices
```sql
CREATE TABLE notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                   -- Notice title
    content TEXT NOT NULL,                 -- Notice content
    icon TEXT DEFAULT 'bell',              -- Notice icon
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Publication time
    created_by TEXT NOT NULL               -- Publisher
);
```

### 6. activities
```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                   -- Activity title
    description TEXT NOT NULL,             -- Activity description
    date TEXT NOT NULL,                    -- Activity date
    time TEXT NOT NULL,                    -- Activity time
    location TEXT NOT NULL,                -- Activity location
    status TEXT DEFAULT 'Registration Open' -- Activity status
);
```

### 7. admins
```sql
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,         -- Admin username
    password TEXT NOT NULL,                -- Password (encrypted)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Creation time
);
```

## Relationship Diagram
```
residents 1:N utility_bills  (One resident can have multiple bills)
residents 1:N maintenance   (One resident can have multiple maintenance records)
residents 1:N visitors     (One resident can have multiple visitors)
```

## Index Design
```sql
-- Residents table indexes
CREATE INDEX idx_residents_apartment ON residents(apartment_number);
CREATE INDEX idx_residents_phone ON residents(phone_number);

-- Bills table indexes
CREATE INDEX idx_bills_apartment ON utility_bills(apartment_number);
CREATE INDEX idx_bills_status ON utility_bills(status);

-- Visitors table indexes
CREATE INDEX idx_visitors_apartment ON visitors(visit_apartment);
CREATE INDEX idx_visitors_status ON visitors(status);

-- Maintenance table indexes
CREATE INDEX idx_maintenance_apartment ON maintenance(apartment_number);
CREATE INDEX idx_maintenance_status ON maintenance(status);
```

## Important Notes
1. All password fields are encrypted using `werkzeug.security`
2. Timestamps default to current system time
3. Foreign key relationships ensure data integrity
4. Regular database file backups are recommended