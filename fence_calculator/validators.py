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
    Validate all input data for fence calculation requests.

    Args:
        data: Dictionary containing calculation input data

    Returns:
        Dictionary with validated values suitable for downstream use

    Raises:
        ValidationError: If any validation fails
    """
    validated: dict = {}

    # Netting selection (supports legacy yes/no values)
    netting_value = data.get('netting_type', data.get('netting', 'none'))
    netting_str = str(netting_value).strip().lower()
    if netting_str in {'yes', 'true'}:
        netting_str = 'sheep'
    elif netting_str in {'no', 'false', ''}:
        netting_str = 'none'
    validated['netting_type'] = validate_choice(
        netting_str,
        'Netting type',
        ['none', 'sheep', 'deer']
    )

    # Electric outrigger toggle (only meaningful for deer netting)
    outrigger_raw = data.get('electric_outrigger', False)
    if isinstance(outrigger_raw, bool):
        outrigger_bool = outrigger_raw
    elif outrigger_raw in (None, ""):
        outrigger_bool = False
    else:
        outrigger_bool = str(outrigger_raw).strip().lower() in {'1', 'true', 'yes', 'on'}
    validated['electric_outrigger'] = outrigger_bool if validated['netting_type'] == 'deer' else False

    # Fence length (required)
    validated['fence_length'] = validate_positive_decimal(
        data.get('fence_length'),
        'Fence length',
        max_value=Decimal('50000')
    )

    # Optional labor rate
    labor_rate = data.get('labor_rate')
    if labor_rate not in (None, ""):
        validated['labor_rate'] = validate_positive_decimal(
            labor_rate,
            'Labor rate',
            max_value=Decimal('1000')
        )
    else:
        validated['labor_rate'] = None

    # Optional build rate (meters/hour)
    build_rate = data.get('build_rate')
    if build_rate not in (None, ""):
        validated['build_rate'] = validate_positive_decimal(
            build_rate,
            'Build rate',
            max_value=Decimal('1000')
        )
    else:
        validated['build_rate'] = None

    # Optional top wire type
    top_wire_type = data.get('top_wire_type')
    if top_wire_type:
        validated['top_wire_type'] = validate_choice(
            top_wire_type,
            'Top wire type',
            ['standard', 'hot', 'barb']
        )
    else:
        validated['top_wire_type'] = None

    # Optional post spacing (limit deer fences to 10 m, others to 50 m)
    post_spacing = data.get('post_spacing')
    if post_spacing not in (None, ""):
        spacing_limit = Decimal('10') if validated['netting_type'] == 'deer' else Decimal('50')
        validated['post_spacing_override'] = validate_positive_decimal(
            post_spacing,
            'Post spacing',
            max_value=spacing_limit
        )
    else:
        validated['post_spacing_override'] = None

    # Optional wire count (allow 0 when deer netting is used)
    wire_count = data.get('wire_count')
    if wire_count not in (None, ""):
        allow_zero = validated['netting_type'] == 'deer'
        validated['wire_count_override'] = validate_positive_integer(
            wire_count,
            'Wire count',
            max_value=20,
            allow_zero=allow_zero
        )
    else:
        validated['wire_count_override'] = None

    # Optional hot wire count (only relevant when requesting a hot top wire)
    hot_wire_count = data.get('hot_wire_count')
    if validated.get('top_wire_type') == 'hot' and hot_wire_count not in (None, ""):
        hot_wires = validate_positive_integer(
            hot_wire_count,
            'Hot wire count',
            max_value=20
        )
        total_wires = validated.get('wire_count_override')
        if total_wires is not None and total_wires > 0 and hot_wires > total_wires:
            raise ValidationError(
                f'Hot wire count ({hot_wires}) cannot exceed total wire count ({total_wires})'
            )
        validated['hot_wire_count'] = hot_wires
    else:
        validated['hot_wire_count'] = None

    # Optional staples per box
    staples_per_box = data.get('staples_per_box')
    if staples_per_box not in (None, ""):
        validated['staples_per_box'] = validate_positive_integer(
            staples_per_box,
            'Staples per box',
            max_value=100000
        )
    else:
        validated['staples_per_box'] = None

    # Price overrides must be a mapping
    price_overrides = data.get('price_overrides', {})
    if not isinstance(price_overrides, dict):
        raise ValidationError('Price overrides must be a dictionary')
    validated['price_overrides'] = price_overrides

    return validated


def validate_material_update_input(data: dict) -> dict:
    """
    Validate input data for material updates via the settings API.

    Args:
        data: Dictionary containing material update data

    Returns:
        Dictionary with validated values

    Raises:
        ValidationError: If any validation fails
    """
    validated: dict = {}

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
            max_value=Decimal('999999'),
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
                max_value=Decimal('10000')
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

    # Validate optional auto update enabled flag
    auto_update_enabled = data.get('auto_update_enabled')
    if auto_update_enabled is not None:
        if not isinstance(auto_update_enabled, bool):
            raise ValidationError('Auto update enabled must be true or false')
        validated['auto_update_enabled'] = auto_update_enabled
    else:
        validated['auto_update_enabled'] = None

    return validated
