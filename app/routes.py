import math, uuid
from flask import Blueprint, jsonify, request, make_response, abort

receipts_bp = Blueprint('receipts', __name__, url_prefix='/receipts')

receipts_data = {}

def generate_id():
    receipt_id = str(uuid.uuid4())
    return receipt_id

def name_points(retailer):
    points = 0
    for letter in retailer:
        if letter.isalnum():
            points += 1
    return points

def dollar_total_points(total):
    points = 0
    total = float(total)
    if total % 1 == 0:
        points += 50
    if total % 0.25 == 0:
        points += 25
    return points 

def description_points(description, price):
    points = 0
    trimmed_length = len(description.strip())

    if trimmed_length % 3 == 0:
        points += math.ceil(float(price) * .2)
    return points

def items_points(items):
    points = 0
    items_count = len(items)

    for item in items:
        description = item['shortDescription']
        price = item['price']
        points += description_points(description, price)

    points += (items_count // 2) * 5
    return points

def date_points(purchaseDate):
    points = 0
    date = float(purchaseDate[8:])
    if date % 2 != 0:
        points += 6
    return points

def time_points(purchaseTime):
    points = 0
    time = float(purchaseTime[0:2])

    if 14 <= time <= 15:
        points += 10
    return points

def get_points(id):
    if id in receipts_data:
        receipt = receipts_data[id]
        return receipt['points']
    else:
        error_msg = f'Invalid id: {id}. Receipt not in database.'
        abort(make_response(error_msg, 400))

def validate_data_fields(request_body):
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    missing_fields = [field for field in required_fields if field not in request_body]

    if missing_fields:
        error_msg = 'Please include all required fields.'
        abort(make_response(error_msg, 400))
    return request_body

@receipts_bp.route('/<id>/points', methods=['GET'])
def handle_receipts(id):
    points = get_points(id)
    return jsonify({'points': points})

@receipts_bp.route('/process', methods=['POST'])
def create_receipt():
    request_body = request.get_json()

    validate_data_fields(request_body)
    
    retailer = request_body['retailer']
    purchase_date = request_body['purchaseDate']
    purchase_time = request_body['purchaseTime']
    items = request_body['items']
    total = request_body['total']

    id = generate_id()
    points = name_points(retailer) + dollar_total_points(total) + items_points(items) + date_points(purchase_date) + time_points(purchase_time)

    new_receipt = {
        'retailer' : retailer,
        'purchaseDate' : purchase_date,
        'purchaseTime' : purchase_time,
        'items' : items,
        'total' : total,
        'points' : points
    }

    receipts_data[id] = new_receipt

    return jsonify({'id':id})