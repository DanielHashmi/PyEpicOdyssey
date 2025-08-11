## Comprehensive Explanation of Each Setting

### Model Configuration (`ConfigDict`)

**`validate_assignment=True`**
- Validates data when you assign new values to fields after creating the model
- Without this, `user.age = "invalid"` would work; with it, it raises a validation error

**`validate_default=True`**
- Validates default values every time you create an instance
- Normally defaults are trusted for performance; this ensures they're always valid

**`strict=False`**
- Enables lax mode where Pydantic tries to coerce compatible types
- `strict=True` would only accept exact type matches

**`coerce_numbers_to_str=True`**
- Allows converting numbers to strings (normally disabled)
- Example: `123` → `"123"` for string fields

**`extra='allow'`**
- Allows extra fields not defined in the model
- Options: `'ignore'` (default), `'forbid'`, `'allow'`

**`str_strip_whitespace=True`**
- Automatically removes leading/trailing whitespace from strings
- `"  hello  "` becomes `"hello"`

**`str_to_lower=False`**
- When `True`, converts all strings to lowercase
- Useful for case-insensitive fields

**`from_attributes=True`**
- Allows creating models from objects with attributes (like ORM instances)
- Replaces V1's `orm_mode=True`

**`populate_by_name=False`**
- Allows population of fields using their Python names even if an alias is set

**`use_enum_values=False`**
- When `True`, serializes enum fields using their values instead of names

**`json_schema_extra={}`**
- Add extra metadata to the generated JSON schema

**`protected_namespaces=('model_',)`**
- Prevents assignment to attributes with these prefixes

**`arbitrary_types_allowed=False`**
- When `True`, allows arbitrary (non-Pydantic) types as fields

### Field Configuration (`Field()`)

**Validation Constraints:**
- `min_length`/`max_length`: String and collection length limits
- `gt`/`ge`/`lt`/`le`: Numeric comparison constraints
- `pattern`: Regular expression validation
- `multiple_of`: Number must be multiple of specified value

**Aliases:**
- `alias`: Name used for both validation and serialization
- `validation_alias`: Only affects input validation
- `serialization_alias`: Only affects output serialization

**Metadata:**
- `description`: Human-readable field description
- `examples`: Example values for documentation
- `title`: Human-readable title

**Special Behaviors:**
- `frozen=True`: Makes field immutable after creation
- `exclude=True`: Excludes field from serialization
- `union_mode`: Controls how unions are validated
- `default_factory`: Callable to generate default value at runtime

### Custom Validation

**`@field_validator`**
- Validates individual fields with custom logic
- Replaces V1's `@validator`

**`@model_validator`** 
- Validates the entire model after all fields are processed
- Can access multiple fields for cross-field validation

### Custom Serialization

**`@field_serializer`**
- Customizes how individual fields are serialized to dict/JSON

**`@model_serializer`**
- Customizes how the entire model is serialized
- Can add computed fields or modify the output structure

### Special Types

**`PositiveInt`**: Integer that must be > 0  

**`EmailStr`**: Validates email format (requires `email-validator`)  

**`HttpUrl`**: Validates and normalizes URLs  

**`SecretStr`**: Hides sensitive data in output  

**`StrictInt`/`StrictStr`**: Only accepts exact type matches  

**`UUID`**: Validates and parses UUID strings  

**`conlist`**: List with length and item constraints  

**`constr`**: String with length and pattern constraints  

**`Json`**: Field that parses and validates JSON data  
