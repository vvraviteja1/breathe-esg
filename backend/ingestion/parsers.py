import pandas as pd
import math
import json
from datetime import date, datetime
from decimal import Decimal

EMISSION_FACTORS = {
    'Diesel':           {'factor': Decimal('2.68839'), 'unit': 'kgCO2e/litre', 'scope': 1},
    'Petrol':           {'factor': Decimal('2.31563'), 'unit': 'kgCO2e/litre', 'scope': 1},
    'Natural Gas':      {'factor': Decimal('2.04268'), 'unit': 'kgCO2e/m3',    'scope': 1},
    'Grid Electricity': {'factor': Decimal('0.20704'), 'unit': 'kgCO2e/kWh',   'scope': 2},
    'Air Travel':       {'factor': Decimal('0.19500'), 'unit': 'kgCO2e/km',    'scope': 3},
    'Hotel Stay':       {'factor': Decimal('0.06900'), 'unit': 'kgCO2e/night', 'scope': 3},
    'Ground Transport': {'factor': Decimal('0.14200'), 'unit': 'kgCO2e/km',    'scope': 3},
}

SAP_UNIT_MAP = {
    'L': 'litre', 'LTR': 'litre', 'LT': 'litre',
    'GAL': 'litre',
    'KG': 'kg',
    'M3': 'm3', 'MTQ': 'm3',
}

MATERIAL_MAP = {
    'DIESEL': 'Diesel', 'DSL': 'Diesel', 'HSD': 'Diesel',
    'PETROL': 'Petrol', 'PTR': 'Petrol', 'MS': 'Petrol',
    'GAS': 'Natural Gas', 'LPG': 'Natural Gas', 'NG': 'Natural Gas',
}

AIRPORTS = {
    'DEL': (28.5665, 77.1031), 'BOM': (19.0896, 72.8656),
    'BLR': (13.1986, 77.7066), 'HYD': (17.2403, 78.4294),
    'MAA': (12.9900, 80.1693), 'CCU': (22.6546, 88.4467),
    'LHR': (51.4700, -0.4543), 'JFK': (40.6413, -73.7781),
    'DXB': (25.2532, 55.3657), 'SIN': (1.3644, 103.9915),
    'CDG': (49.0097,  2.5479), 'FRA': (50.0379,  8.5622),
    'NRT': (35.7720, 140.3929), 'SYD': (-33.9399, 151.1753),
}


def clean_raw(row_dict):
    """Convert NaN/inf floats to None so the dict is valid JSON."""
    cleaned = {}
    for k, v in row_dict.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


def haversine_km(code1, code2):
    if code1 not in AIRPORTS or code2 not in AIRPORTS:
        return None
    lat1, lon1 = map(math.radians, AIRPORTS[code1])
    lat2, lon2 = map(math.radians, AIRPORTS[code2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return round(6371 * 2 * math.asin(math.sqrt(a)), 2)


def parse_date(val):
    for fmt in ('%Y%m%d', '%d.%m.%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {val}")


def normalize_volume(value, unit):
    unit = unit.strip().upper()
    value = float(value)
    if unit == 'GAL':
        value *= 3.785
        unit = 'litre'
    elif unit in ('L', 'LTR', 'LT'):
        unit = 'litre'
    elif unit in ('M3', 'MTQ'):
        unit = 'm3'
    return round(value, 4), unit


def safe_str(val):
    s = str(val).strip()
    return '' if s.lower() == 'nan' else s


def safe_float(val, default):
    s = safe_str(val)
    return float(s) if s else default


# ═══════════════════════════════════════════════════════════
# SAP PARSER
# ═══════════════════════════════════════════════════════════
def parse_sap(file) -> tuple[list, list]:
    records, errors = [], []
    try:
        df = pd.read_csv(file, dtype=str)
        df.columns = [c.strip().upper() for c in df.columns]
    except Exception as e:
        return [], [{'row': 0, 'error': f'File read error: {e}'}]

    required = {'WERKS', 'MATNR', 'MENGE', 'MEINS', 'BLDAT'}
    missing = required - set(df.columns)
    if missing:
        return [], [{'row': 0, 'error': f'Missing columns: {missing}'}]

    for i, row in df.iterrows():
        raw = clean_raw(row.to_dict())
        try:
            material = str(row.get('MATNR', '')).upper()
            category = next(
                (v for k, v in MATERIAL_MAP.items() if k in material), None)
            if not category:
                raise ValueError(f"Unknown material: {material}")

            vol, unit = normalize_volume(row['MENGE'], row['MEINS'])
            period = parse_date(row['BLDAT'])
            ef_info = EMISSION_FACTORS[category]
            co2e = round(vol * float(ef_info['factor']), 4)

            records.append({
                'scope': ef_info['scope'],
                'category': category,
                'activity_value': vol,
                'activity_unit': unit,
                'emission_factor': float(ef_info['factor']),
                'emission_factor_source': 'DEFRA 2024',
                'co2e_kg': co2e,
                'period_start': period,
                'period_end': period,
                'facility_code': row.get('WERKS', ''),
                'country': row.get('COUNTRY', 'IN'),
                'source_row_id': str(i),
                'raw_data': raw,
            })
        except Exception as e:
            errors.append({'row': i + 2, 'error': str(e), 'data': raw})

    return records, errors


# ═══════════════════════════════════════════════════════════
# UTILITY PARSER
# ═══════════════════════════════════════════════════════════
def parse_utility(file) -> tuple[list, list]:
    records, errors = [], []
    try:
        df = pd.read_csv(file, dtype=str)
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception as e:
        return [], [{'row': 0, 'error': f'File read error: {e}'}]

    for i, row in df.iterrows():
        raw = clean_raw(row.to_dict())
        try:
            kwh = float(row['consumption_kwh'])
            start = parse_date(row['period_start'])
            end = parse_date(row['period_end'])
            ef = EMISSION_FACTORS['Grid Electricity']
            co2e = round(kwh * float(ef['factor']), 4)

            records.append({
                'scope': 2,
                'category': 'Grid Electricity',
                'activity_value': kwh,
                'activity_unit': 'kWh',
                'emission_factor': float(ef['factor']),
                'emission_factor_source': 'DEFRA 2024',
                'co2e_kg': co2e,
                'period_start': start,
                'period_end': end,
                'facility_code': row.get('site_name', ''),
                'country': row.get('country', 'IN'),
                'source_row_id': str(i),
                'raw_data': raw,
            })
        except Exception as e:
            errors.append({'row': i + 2, 'error': str(e), 'data': raw})

    return records, errors


# ═══════════════════════════════════════════════════════════
# TRAVEL PARSER
# ═══════════════════════════════════════════════════════════
def parse_travel(file) -> tuple[list, list]:
    records, errors = [], []
    try:
        df = pd.read_csv(file, dtype=str)
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception as e:
        return [], [{'row': 0, 'error': f'File read error: {e}'}]

    for i, row in df.iterrows():
        raw = clean_raw(row.to_dict())
        try:
            exp_type = safe_str(row.get('expense_type', '')).upper()

            if 'FLIGHT' in exp_type:
                origin = safe_str(row.get('origin', '')).upper()
                dest = safe_str(row.get('destination', '')).upper()
                dist = haversine_km(origin, dest)
                if dist is None:
                    raise ValueError(f"Unknown airport code: {origin} or {dest}")
                ef = EMISSION_FACTORS['Air Travel']
                co2e = round(dist * float(ef['factor']), 4)
                category = 'Air Travel'
                activity_value, activity_unit = dist, 'km'

            elif 'HOTEL' in exp_type:
                nights = safe_float(row.get('hotel_nights'), 1)
                ef = EMISSION_FACTORS['Hotel Stay']
                co2e = round(nights * float(ef['factor']), 4)
                category = 'Hotel Stay'
                activity_value, activity_unit = nights, 'nights'

            elif 'GROUND' in exp_type:
                dist = safe_float(row.get('distance_km'), 50)
                ef = EMISSION_FACTORS['Ground Transport']
                co2e = round(dist * float(ef['factor']), 4)
                category = 'Ground Transport'
                activity_value, activity_unit = dist, 'km'

            else:
                raise ValueError(f"Unknown expense type: {exp_type}")

            dep_raw = safe_str(row.get('departure_date', ''))
            ret_raw = safe_str(row.get('return_date', ''))
            dep_date = parse_date(dep_raw) if dep_raw else date.today()
            ret_date = parse_date(ret_raw) if ret_raw else dep_date

            ef_info = EMISSION_FACTORS[category]
            records.append({
                'scope': 3,
                'category': category,
                'activity_value': activity_value,
                'activity_unit': activity_unit,
                'emission_factor': float(ef_info['factor']),
                'emission_factor_source': 'DEFRA 2024',
                'co2e_kg': co2e,
                'period_start': dep_date,
                'period_end': ret_date,
                'facility_code': None,
                'country': safe_str(row.get('country', '')) or 'IN',
                'source_row_id': str(i),
                'raw_data': raw,
            })
        except Exception as e:
            errors.append({'row': i + 2, 'error': str(e), 'data': raw})

    return records, errors