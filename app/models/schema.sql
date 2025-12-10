-- Vendors table
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tax_id TEXT UNIQUE,
    address TEXT,
    phone TEXT,
    email TEXT,
    payment_terms TEXT DEFAULT 'NET30',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table
CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,  -- UUID
    vendor_id INTEGER,
    vendor_name TEXT NOT NULL,
    vendor_tax_id TEXT,
    invoice_number TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    currency TEXT DEFAULT 'VND',
    subtotal REAL NOT NULL,
    discount_total REAL DEFAULT 0,
    tax_total REAL NOT NULL,
    total_amount REAL NOT NULL,
    notes TEXT,
    payment_terms TEXT,
    
    -- File tracking
    pdf_path TEXT NOT NULL,
    pdf_hash TEXT,  -- SHA256 for duplicate detection
    
    -- Processing metadata
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extracted_at TIMESTAMP,
    validated_at TIMESTAMP,
    automated_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Status tracking
    status TEXT DEFAULT 'pending',  
    -- pending, extracted, validated, automated, completed, failed
    
    -- Quality metrics
    extraction_confidence REAL,
    validation_errors INTEGER DEFAULT 0,
    manual_corrections INTEGER DEFAULT 0,
    
    -- Gemini API tracking
    gemini_cost_usd REAL,
    processing_time_ms INTEGER,
    
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    UNIQUE(vendor_id, invoice_number, invoice_date)
);

-- Invoice items table
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT,
    unit_price REAL NOT NULL,
    discount_percent REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    tax_percent REAL DEFAULT 10,
    tax_amount REAL NOT NULL,
    subtotal REAL NOT NULL,
    total REAL NOT NULL,
    
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    UNIQUE(invoice_id, line_number)
);

-- Automation runs table
CREATE TABLE IF NOT EXISTS automation_runs (
    id TEXT PRIMARY KEY,  -- UUID
    invoice_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running',  -- running, paused, completed, failed
    error_message TEXT,
    screenshots_path TEXT,  -- JSON array of screenshot paths
    actions_log TEXT,  -- JSON log of all actions taken
    
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user TEXT DEFAULT 'system',
    action TEXT NOT NULL,  -- upload, extract, validate, correct, automate, complete
    entity_type TEXT NOT NULL,  -- invoice, item, automation
    entity_id TEXT NOT NULL,
    details TEXT,  -- JSON details of the action
    status TEXT,  -- success, warning, error
    ip_address TEXT,
    user_agent TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date DESC);
CREATE INDEX IF NOT EXISTS idx_invoices_vendor ON invoices(vendor_id);
CREATE INDEX IF NOT EXISTS idx_invoices_pdf_hash ON invoices(pdf_hash);
CREATE INDEX IF NOT EXISTS idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);
