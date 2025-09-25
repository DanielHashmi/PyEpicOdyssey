from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Union, Annotated, Any
from enum import Enum

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    field_serializer,
    model_serializer,
    ValidationError,
    PositiveInt,
    EmailStr,
    HttpUrl,
    SecretStr
)

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Address(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically remove leading/trailing spaces from string inputs
        validate_assignment=True,   # Validate field values when attributes are set after model creation
        extra='forbid'              # Raise ValidationError when unknown fields are provided in input data
    )

    street: str = Field(
        min_length=1, max_length=100
    )  # Ensure street is between 1-100 characters
    city: str = Field(
        min_length=1, max_length=50
    )  # Ensure city is between 1-50 characters
    postal_code: str = Field(
        pattern=r'^\d{5}(-\d{4})?$'
    )  # US postal code validation (5 digits or 5+4 format)
    country: str = Field(
        default="USA", frozen=True
    )  # Default "USA", immutable after creation

class User(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,      # Validate new values when fields are modified after instantiation
        validate_default=True,         # Validate default values on every model creation for safety
        strict=False,                  # Enable lax mode allowing type coercion (string "123" -> int 123)
        coerce_numbers_to_str=True,    # Allow number-to-string conversion (123 -> "123")
        extra='allow',                 # Permit additional fields not defined in model schema
        str_strip_whitespace=True,     # Automatically trim whitespace from all string inputs
        str_to_lower=False,            # Preserve original string casing (set True for lowercase conversion)
        str_max_length=1000,           # Global string length limit for all string fields
        ser_json_timedelta='iso8601',  # Serialize timedelta objects in ISO8601 format
        ser_json_bytes='base64',       # Serialize bytes objects as base64 encoded strings
        title="User Model",            # Human-readable model name in generated schemas
        use_attribute_docstrings=True, # Include docstrings in generated JSON schema
        frozen=False,                  # Allow field modification after model creation (True makes immutable)
        populate_by_name=True,         # Accept both field names and aliases during validation
        from_attributes=True           # Create models from objects with attributes (replaces orm_mode)
    )

    id: PositiveInt = Field(
        description="Unique user identifier",
        examples=[1, 42, 123],
        gt=0, le=999999
    )  # PositiveInt type with constraints

    name: str = Field(
        min_length=2, max_length=50,
        description="User's full name",
        alias="full_name"
    )  # String field with length constraints and alias

    email: EmailStr = Field(
        description="User's email address",
        validation_alias="email_address"
    )  # EmailStr validation with input-only alias

    password: SecretStr = Field(
        min_length=8,
        description="User password (will be hidden in output)"
    )  # SecretStr field with min_length=8

    role: UserRole = Field(
        default=UserRole.USER
    )  # Enum field with default value

    is_active: bool = Field(
        default=True
    )  # Boolean field with default=True

    age: Optional[int] = Field(
        default=None, ge=0, le=150,
        description="User's age in years"
    )  # Optional integer with age constraints

    balance: Decimal = Field(
        default=Decimal('0.00'),
        max_digits=10, decimal_places=2,
        description="Account balance"
    )  # Decimal field with precision constraints

    created_at: datetime = Field(
        default_factory=datetime.now
    )  # Datetime field with factory function

    birth_date: Optional[date] = None  # Optional date field for birth date tracking

    website: Optional[HttpUrl] = None  # Optional HttpUrl field for website validation

    address: Optional[Address] = None  # Optional nested model field for address composition

    tags: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="User tags"
    )  # List field with max_length=10 constraint

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional user metadata"
    )  # Flexible metadata dict field

    phone: Union[str, int] = Field(
        description="Phone number as string or int",
        union_mode='left_to_right'
    )  # Union field for phone number flexibility

    score: Annotated[float, Field(ge=0.0, le=100.0, multiple_of=0.1)] = 0.0  # Float field with range and precision constraints

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.replace(' ', '').isalpha():
            raise ValueError('Name must contain only letters and spaces')
        return v.title()  # Auto-title case

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        return [tag.lower().strip() for tag in v if tag.strip()]  # Clean and normalize tag list

    @model_validator(mode='after')
    def validate_age_birth_date(self) -> 'User':
        if self.age is not None and self.birth_date is not None:
            calculated_age = (date.today() - self.birth_date).days // 365
            if abs(calculated_age - self.age) > 1:
                raise ValueError('Age and birth date do not match')
        return self  # Cross-field  validation between age and birth_date

    @field_serializer('password')
    def serialize_password(self, value: SecretStr) -> str:
        return "***HIDDEN***"  # Hide password content in output

    @model_serializer(mode='wrap')
    def serialize_model(self, serializer, info):
        data = serializer(self)
        data['display_name'] = f"{self.name} ({self.role.value})"
        return data  # Inject computed display_name field in output

if __name__ == "__main__":
    user_data = {
        "id": "123",  # String to int coercion
        "full_name": "  john doe  ",  # Whitespace stripping + title casing
        "email_address": "john@example.com",  # Email validation
        "password": "secretpassword123",  # Secret string handling
        "age": "25",  # String to int coercion
        "balance": "1234.56",  # String to Decimal coercion
        "birth_date": "1998-01-01",  # String to date coercion
        "website": "https://johndoe.com",  # String to HttpUrl coercion
        "phone": 1234567890,  # Union type handling
        "tags": ["  Developer  ", "Python", "  "],  # List cleaning
        "score": "85.5",  # String to float coercion
        "metadata": {"department": "engineering", "level": 3},  # Dict handling
        "extra_field": "This will be allowed due to extra='allow'"  # Extra field allowance
    }

    try:
        user = User(**user_data)
        print("User created successfully!")
        print(f"Serialized: {user.model_dump()}")
        print(f"JSON: {user.model_dump_json(indent=2)}")

    except ValidationError as e:
        print(f"Validation error: {e}")
