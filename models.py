from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
import time

# Create the database instance but don't attach it to an app yet
db = SQLAlchemy()

class Company(db.Model):
    """Stores the core, unique information for a company."""
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    country_code = db.Column(db.String(5), nullable=False, index=True) # e.g., 'us', 'uk'

    # A company is unique by its symbol within a country
    __table_args__ = (UniqueConstraint('symbol', 'country_code', name='_symbol_country_uc'),)

    # Relationships
    profile = db.relationship('CompanyProfile', backref='company', uselist=False, cascade="all, delete-orphan")
    financials = db.relationship('FinancialStatement', backref='company', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company {self.symbol} ({self.country_code.upper()})>"

class CompanyProfile(db.Model):
    """Stores detailed profile information for a company."""
    __tablename__ = 'company_profile'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False, unique=True)
    
    exchange = db.Column(db.String(50))
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    full_time_employees = db.Column(db.Integer)
    market_cap_usd = db.Column(db.BigInteger)

    # Caching timestamp
    last_updated_ts = db.Column(db.Integer, nullable=False, default=lambda: int(time.time()))

    def is_stale(self, timeout):
        """Checks if the cache for this entry has expired."""
        return (time.time() - self.last_updated_ts) > timeout

class FinancialStatement(db.Model):
    """Stores year-wise financial data for a company."""
    __tablename__ = 'financial_statement'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    
    revenue_usd = db.Column(db.BigInteger)
    profit_usd = db.Column(db.BigInteger)
    share_capital_usd = db.Column(db.BigInteger)

    __table_args__ = (UniqueConstraint('company_id', 'year', name='_company_year_uc'),)

    def __repr__(self):
        return f"<FinancialStatement {self.company.symbol} Year: {self.year}>"