"""
Custom validators for the fence calculator application.
Provides reusable validation functions with consistent error messages.
"""

from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, Any


class ValidationError(Exception):
    """Custom validation error for fence calculator."""
    pass


def validate_positive_decimal(
    value: Any, 
    field_name: str, 
    max_value: Optional[Decimal] = None,
    allow_zero: bool = False
) -> Decimal:
    """
    Validate that a value is a positive decimal.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        max_value: Optional maximum allowed value
        allow_zero: Whether to allow zero values
        
    Returns:
        Validated Decimal value
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None or value == "":
        raise ValidationError(f"{field_name} is required")
    
    try:
        decimal_value = Decimal(str(value))
    except (ValueError, TypeError, InvalidOperation):
        raise ValidationError(f"Invalid {field_name.lower()} format")
    
    min_value = Decimal('0') if allow_zero else Decimal('0.01')
    if decimal_value < min_value:
        if allow_zero:
            raise ValidationError(f"{field_name} cannot be negative")
        else:
            raise ValidationError(f"{field_name} must be greater than 0")
    
    if max_value and decimal_value > max_value:
        raise ValidationError(f"{field_name} cannot exceed {max_value}")
    
    return decimal_value


def validate_positive_integer(
    value: Any, 
    field_name: str, 
    max_value: Optional[int] = None,
    allow_zero: bool = False
) -> int:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        max_value: Optional maximum allowed value
        allow_zero: Whether to allow zero values
        
    Returns:
        Validated integer value
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None or value == "":
        raise ValidationError(f"{field_name} is required")
    
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid {field_name.lower()} format")
    
    min_value = 0 if allow_zero else 1
    if int_value < min_value:
        if allow_zero:
            raise ValidationError(f"{field_name} cannot be negative")
        else:
            raise ValidationError(f"{field_name} must be greater than 0")
    
    if max_value and int_value > max_value:
        raise ValidationError(f"{field_name} cannot exceed {max_value}")
    
    return int_value


def validate_choice(value: Any, field_name: str, choices: list) -> str:
    """
    Validate that a value is one of the allowed choices.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        choices: List of allowed choices
        
    Returns:
        Validated string value
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None or value == "":
        raise ValidationError(f"{field_name} is required")
    
    str_value = str(value)
    if str_value not in choices:
        choices_str = '", "'.join(choices)
        raise ValidationError(f'{field_name} must be one of: "{choices_str}"')
    
    return str_value


def validate_string_length(
    value: Any, 
    field_name: str, 
    max_length: int,
    required: bool = True
) -> Optional[str]:
    """
    Validate string length.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        required: Whether the field is required
        
    Returns:
        Validated string value or None
        
    Raises:
        ValidationError: If validation fails
    """
    if value is None or value == "":
        if required:
            raise ValidationError(f"{field_name} is required")
        return None
    
    str_value = str(value)
    if len(str_value) > max_length:
        raise ValidationError(f"{field_name} cannot exceed {max_length} characters")
    
    return str_value


def validate_fence_calculation_input(data: dict) -> dict:
    """
    Validate all input data for fence calculation.
    
    Args:
        data: Dictionary containing calculation input data
        
    Returns:
        Dictionary with validated values
        
    Raises:
        ValidationError: If any validation fails
    """
    validated = {}
    
    # Validate netting choice
    validated['netting'] = validate_choice(
        data.get('netting', 'no'), 
        'Netting', 
        ['yes', 'no']
    )
    
    # Validate fence length
    validated['fence_length'] = validate_positive_decimal(
        data.get('fence_length'),
        'Fence length',
        max_value=Decimal('50000')  # 50km max
    )
    
    # Validate optional labor rate
    labor_rate = data.get('labor_rate')
    if labor_rate not in (None, ""):
        validated['labor_rate'] = validate_positive_decimal(
            labor_rate,
            'Labor rate',
            max_value=Decimal('1000')  # $1000/hour max
        )
    else:
        validated['labor_rate'] = None
    
    # Validate optional top wire type
    top_wire_type = data.get('top_wire_type')
    if top_wire_type:
        validated['top_wire_type'] = validate_choice(
            top_wire_type,
            'Top wire type',
            ['standard', 'hot', 'barb']
        )
    else:
        validated['top_wire_type'] = None
    
    # Validate optional post spacing
    post_spacing = data.get('post_spacing')
    if post_spacing not in (None, ""):
        validated['post_spacing_override'] = validate_positive_decimal(
            post_spacing,
            'Post spacing',
            max_value=Decimal('50')  # 50m max
        )
    else:
        validated['post_spacing_override'] = None
    
    # Validate optional wire count
    wire_count = data.get('wire_count')
    if wire_count not in (None, ""):
        validated['wire_count_override'] = validate_positive_integer(
            wire_count,
            'Wire count',
            max_value=20  # 20 wires max
        )
    else:
        validated['wire_count_override'] = None
    
    # Validate optional hot wire count (only if top wire type is hot)
    hot_wire_count = data.get('hot_wire_count')
    if validated.get('top_wire_type') == 'hot' and hot_wire_count not in (None, ""):
        hot_wires = validate_positive_integer(
            hot_wire_count,
            'Hot wire count',
            max_value=20  # 20 wires max
        )
        total_wires = validated.get('wire_count_override')
        if total_wires and hot_wires > total_wires:
            raise ValidationError(f'Hot wire count ({hot_wires}) cannot exceed total wire count ({total_wires})')
        validated['hot_wire_count'] = hot_wires
    else:
        validated['hot_wire_count'] = None
    
    # Validate price overrides
    price_overrides = data.get('price_overrides', {})
    if not isinstance(price_overrides, dict):
        raise ValidationError('Price overrides must be a dictionary')
    validated['price_overrides'] = price_overrides
    
    return validated


def validate_material_update_input(data: dict) -> dict:
    """
    Validate input data for material updates.
    
    Args:
        data: Dictionary containing material update data
        
    Returns:
        Dictionary with validated values
        
    Raises:
        ValidationError: If any validation fails
    """
    validated = {}
    
    # Validate material ID
    validated['material_id'] = validate_positive_integer(
        data.get('id'),
        'Material ID'
    )
    
    # Validate optional current price
    current_price = data.get('current_price')
    if current_price is not None:
        validated['current_price'] = validate_positive_decimal(
            current_price,
            'Current price',
            max_value=Decimal('999999'),  # $999,999 max
            allow_zero=True
        )
    else:
        validated['current_price'] = None
    
    # Validate optional roll length
    roll_length = data.get('roll_length')
    if roll_length is not None:
        if roll_length == '':
            validated['roll_length'] = None
        else:
            validated['roll_length'] = validate_positive_decimal(
                roll_length,
                'Roll length',
                max_value=Decimal('10000')  # 10km max
            )
    else:
        validated['roll_length'] = None
    
    # Validate optional price source
    price_source = data.get('price_source')
    if price_source is not None:
        validated['price_source'] = validate_string_length(
            price_source,
            'Price source',
            max_length=200,
            required=False
        )
    else:
        validated['price_source'] = None
    
    # Validate optional auto update enabled
    auto_update_enabled = data.get('auto_update_enabled')
    if auto_update_enabled is not None:
        if not isinstance(auto_update_enabled, bool):
            raise ValidationError('Auto update enabled must be true or false')
        validated['auto_update_enabled'] = auto_update_enabled
    else:
        validated['auto_update_enabled'] = None
    
    return validated
