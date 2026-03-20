from django import template
import locale

register = template.Library()

@register.filter(name='indian_currency')
def indian_currency(value):
    """
    Formats a number as Indian Rupee (₹) with Indian numbering system (Lakhs, Crores).
    Example: 1234567.89 -> ₹12,34,567.89
    """
    if value is None or value == '':
        return '₹0'
    
    try:
        # Convert to float if it's a string or other numeric type
        amount = float(value)
    except (ValueError, TypeError):
        return f'₹{value}'

    # Format the number manually for Indian style (3, 2, 2 grouping)
    # 1. Handle decimal part
    s = f"{amount:.2f}"
    parts = s.split('.')
    main_number = parts[0]
    decimal_part = parts[1]
    
    # 2. Handle the main number part for Indian grouping
    is_negative = main_number.startswith('-')
    if is_negative:
        main_number = main_number[1:]
        
    # Reverse it to handle from the right
    main_number = main_number[::-1]
    
    # First comma after 3 digits
    result = main_number[:3]
    remaining = main_number[3:]
    
    # Subsequent commas after every 2 digits
    while len(remaining) > 0:
        result += ',' + remaining[:2]
        remaining = remaining[2:]
    
    # Reverse back
    formatted_main = result[::-1]
    
    # Add negative sign back
    if is_negative:
        formatted_main = '-' + formatted_main
    
    # Remove leading comma if any
    if formatted_main.startswith(',') or formatted_main.startswith('-,'):
        formatted_main = formatted_main.replace(',', '', 1)
        
    return f'₹{formatted_main}.{decimal_part}'

@register.filter(name='rupee_no_decimal')
def rupee_no_decimal(value):
    """Formats a number as Indian Rupee (₹) without decimal part."""
    formatted = indian_currency(value)
    if '.' in formatted:
        return formatted.split('.')[0]
    return formatted
