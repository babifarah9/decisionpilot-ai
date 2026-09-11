"""Synthetic provider inventory. Prices are illustrative USD totals, not live quotes."""
from datetime import date, timedelta
import math


def inventory():
    day = date.today() + timedelta(days=4)
    return [
        dict(id='central-0900', provider='AutoCare Central', slot=f'{day} 09:00', cost=149.0, rating=4.7),
        dict(id='northside-1100', provider='Northside Motors', slot=f'{day} 11:00', cost=165.0, rating=4.9),
        dict(id='central-0830', provider='AutoCare Central', slot=f'{day + timedelta(days=1)} 08:30', cost=139.0, rating=4.7),
        dict(id='quick-1400', provider='QuickService Garage', slot=f'{day + timedelta(days=1)} 14:00', cost=125.0, rating=4.4),
    ]


def rank(candidates, budget=180.0, daypart='morning'):
    if not isinstance(budget, (int, float)) or not math.isfinite(budget) or not 1 <= budget <= 1000:
        raise ValueError('Budget must be between $1 and $1,000.')
    if daypart not in ('morning', 'any'):
        raise ValueError('Unsupported appointment preference.')
    results = []
    for item in candidates:
        c = dict(item)
        c['eligible'] = c['cost'] < budget and (daypart == 'any' or int(c['slot'][11:13]) < 12)
        c['score'] = round(100 * (0.5 * c['rating'] / 5 + 0.5 * max(0, 1 - c['cost'] / budget)), 2)
        c['note'] = 'Eligible' if c['eligible'] else ('Outside budget' if c['cost'] >= budget else 'Afternoon appointment')
        results.append(c)
    return sorted(results, key=lambda c: (not c['eligible'], -c['score'], c['cost'], c['slot'], c['id']))
