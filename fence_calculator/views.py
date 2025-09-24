from __future__ import annotations
from decimal import Decimal, InvalidOperation
from typing import Any, Dict
import decimal
import json
import logging

from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import FenceType, Material, FenceCalculation
from .utils import calculate_fence_requirements, generate_pdf, generate_excel
from .validators import validate_fence_calculation_input, validate_material_update_input, ValidationError
from . import scraping


def index(request: HttpRequest) -> HttpResponse:
    fence_types = FenceType.objects.filter(is_active=True).order_by('display_name')
    recent_calcs = FenceCalculation.objects.order_by('-created_at')[:10]
    return render(request, 'fence_calculator/index.html', {
        'fence_types': fence_types,
        'recent_calcs': recent_calcs,
        'default_labor_rate': settings.LABOR_RATE_PER_HOUR,
    })


def calculate(request: HttpRequest) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        # Parse request data - handle both JSON and form data
        content_type = request.content_type or ''
        if 'application/json' in content_type:
            try:
                payload = json.loads(request.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        else:
            # Handle form data (multipart/form-data or application/x-www-form-urlencoded)
            payload = request.POST

        # Validate input using our validation utility
        try:
            validated_data = validate_fence_calculation_input(payload)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        # Select fence type based on netting option
        netting = validated_data['netting']
        if netting == 'yes':
            fence_type = FenceType.objects.filter(name='deer', is_active=True).first()
        else:
            fence_type = FenceType.objects.filter(name='2_wire_electric', is_active=True).first()
            
        if not fence_type:
            return JsonResponse({'error': 'No suitable fence type found'}, status=400)
            
    except Exception as e:
        # Log unexpected errors for debugging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in calculate view: {e}", exc_info=True)
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

    # fence_type is already selected above based on netting option

    # Ensure a session key exists
    if not request.session.session_key:
        request.session.create()

    results = calculate_fence_requirements(
        fence_type=fence_type,
        fence_length=validated_data['fence_length'],
        labor_rate=validated_data['labor_rate'],
        price_overrides=validated_data['price_overrides'],
        top_wire_type=validated_data['top_wire_type'],
        post_spacing_override=validated_data['post_spacing_override'],
        wire_count_override=validated_data['wire_count_override'],
        hot_wire_count=validated_data.get('hot_wire_count'),
        staples_per_box=validated_data.get('staples_per_box'),
    )

    calc = FenceCalculation.objects.create(
        fence_type=fence_type,
        fence_length=validated_data['fence_length'],
        posts_required=results['posts_required'],
        wire_length_meters=Decimal(str(results['wire_length_meters'])),
        wire_rolls_required=Decimal(str(results['wire_rolls_required'])),
        labor_hours=Decimal(str(results['labor_hours'])),
        labor_rate_per_hour=Decimal(str(results['labor_rate_per_hour'])),
        labor_cost=Decimal(str(results['labor_cost'])),
        material_costs=results['material_costs'],
        total_material_cost=Decimal(str(results['total_material_cost'])),
        total_cost=Decimal(str(results['total_cost'])),
        price_overrides=validated_data['price_overrides'],
        user_session=request.session.session_key or '',
    )

    results['calculation_id'] = calc.pk
    return JsonResponse(results)


def calculation_detail(request: HttpRequest, pk: int) -> HttpResponse:
    calc = get_object_or_404(FenceCalculation, pk=pk)
    return render(request, 'fence_calculator/calculation_detail.html', {'calc': calc})


def export_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    calc = get_object_or_404(FenceCalculation, pk=pk)
    pdf_bytes = generate_pdf(calc)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    # Use a unique filename (current timestamp) to avoid client caching old downloads
    ts = timezone.localtime(timezone.now()).strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename=fence_calculation_{pk}_{ts}.pdf'
    # Cache-busting headers
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def export_excel(request: HttpRequest, pk: int) -> HttpResponse:
    calc = get_object_or_404(FenceCalculation, pk=pk)
    xlsx_bytes = generate_excel(calc)
    response = HttpResponse(xlsx_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    # Use a unique filename (timestamp) to avoid client caching old downloads
    ts = timezone.localtime(calc.created_at).strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename=fence_calculation_{pk}_{ts}.xlsx'
    # Cache-busting headers
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ---- APIs ---- #

def api_fence_types(request: HttpRequest) -> JsonResponse:
    items = list(FenceType.objects.filter(is_active=True).values('id', 'name', 'display_name', 'post_spacing', 'wire_count'))
    return JsonResponse({'fence_types': items})


def api_materials(request: HttpRequest) -> JsonResponse:
    items = list(Material.objects.filter(is_active=True).values('id', 'name', 'unit', 'default_price', 'current_price'))
    return JsonResponse({'materials': items})


# ---- Settings Views/APIs ---- #

def settings_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'fence_calculator/settings.html')


def settings_api_materials(request: HttpRequest) -> JsonResponse:
    items = list(Material.objects.all().values('id', 'name', 'unit', 'current_price', 'roll_length', 'price_source', 'price_source_url', 'last_price_update', 'auto_update_enabled'))
    # Convert datetimes to ISO
    for it in items:
        if it['last_price_update']:
            it['last_price_update'] = it['last_price_update'].isoformat()
    return JsonResponse({'materials': items})


@api_view(['POST'])
def settings_api_update_material(request: HttpRequest) -> Response:
    try:
        # Validate input using our validation utility
        try:
            validated_data = validate_material_update_input(request.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)
        
        # Get the material
        try:
            material = Material.objects.get(id=validated_data['material_id'])
        except Material.DoesNotExist:
            return Response({'error': 'Material not found'}, status=404)

        # Update fields with validated data
        if validated_data['current_price'] is not None:
            material.current_price = validated_data['current_price']
        
        if validated_data['roll_length'] is not None:
            material.roll_length = validated_data['roll_length']
        
        if validated_data['price_source'] is not None:
            material.price_source = validated_data['price_source']
        
        if validated_data['auto_update_enabled'] is not None:
            material.auto_update_enabled = validated_data['auto_update_enabled']

        material.last_price_update = timezone.now()
        material.save()
        
        return Response({
            'success': True,
            'material': {
                'id': material.id,
                'name': material.name,
                'current_price': float(material.current_price) if material.current_price else None,
                'roll_length': float(material.roll_length) if material.roll_length else None,
                'price_source': material.price_source,
                'auto_update_enabled': material.auto_update_enabled,
                'last_price_update': material.last_price_update.isoformat() if material.last_price_update else None
            }
        })
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in settings_api_update_material: {e}", exc_info=True)
        return Response({'error': 'An unexpected error occurred'}, status=500)


def settings_api_scrape(request: HttpRequest) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    updated = scraping.scrape_prices_now()
    return JsonResponse({'updated': updated, 'timestamp': timezone.now().isoformat()})
