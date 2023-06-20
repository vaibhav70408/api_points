import csv
from flask import Flask, request, jsonify
from collections import Counter

app = Flask(__name__)

def read_dataset_from_csv():
    dataset = []
    with open('data.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dataset.append(row)
    return dataset

# API 1: Total items sold in Marketing for the last quarter of the year
@app.route('/api/total_items', methods=['GET'])
def get_total_items():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department', 'Marketting')  # Default department is 'Marketting'

    dataset = read_dataset_from_csv()
    
    # Filter the dataset based on the specified date range and department
    filtered_data = [
        row for row in dataset
        if row['department'] == department and start_date <= row['date'] <= end_date
    ]
    
    # Calculate the total number of seats sold
    total_items_sold = sum(int(row['seats']) for row in filtered_data)
    
    return jsonify({'total_items': total_items_sold})

# API 2: Nth most sold item based on quantity or total price within a specified date range
@app.route('/api/nth_most_total_item', methods=['GET'])
def get_nth_most_total_item():
    item_by = request.args.get('item_by')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    n = int(request.args.get('n'))

    if item_by not in ['quantity', 'price']:
        return jsonify({'error': 'Invalid item_by parameter. Valid options are "quantity" and "price".'}), 400

    dataset = read_dataset_from_csv()

    # Filter the dataset based on the specified date range
    filtered_data = [
        row for row in dataset
        if start_date <= row['date'] <= end_date
    ]

    if item_by == 'quantity':
        sorted_items = sorted(filtered_data, key=lambda x: int(x['seats']), reverse=True)
    else:
        sorted_items = sorted(filtered_data, key=lambda x: float(x['amount']), reverse=True)

    if 1 <= n <= len(sorted_items):
        nth_item = sorted_items[n - 1]['software']
        return jsonify({'nth_item': nth_item})
    else:
        return jsonify({'error': 'Invalid value for n parameter. Must be between 1 and the total number of items.'}), 400



# API 3: Percentage of sold items (seats) department-wise
@app.route('/api/percentage_of_department_wise_sold_items', methods=['GET'])
def get_percentage_of_department_wise_sold_items():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    dataset = read_dataset_from_csv()

    # Filter the dataset based on the specified date range
    filtered_data = [
        row for row in dataset
        if start_date <= row['date'] <= end_date
    ]

    department_counts = {}
    total_count = 0

    # Calculate the count of sold items (seats) for each department
    for row in filtered_data:
        department = row['department']
        seats = int(row['seats'])

        if department in department_counts:
            department_counts[department] += seats
        else:
            department_counts[department] = seats

        total_count += seats

    department_percentages = {}

    # Calculate the percentage of sold items (seats) for each department
    for department, count in department_counts.items():
        percentage = (count / total_count) * 100
        department_percentages[department] = round(percentage, 2)

    return jsonify(department_percentages)



# API 4: Monthly sales for a specific product
@app.route('/api/monthly_sales', methods=['GET'])
def get_monthly_sales():
    product = request.args.get('product')
    year = int(request.args.get('year'))

    dataset = read_dataset_from_csv()

    # Filter the dataset based on the specified product and year
    filtered_data = [
        row for row in dataset
        if row['software'] == product and int(row['date'][:4]) == year
    ]

    # Calculate the monthly sales for the product
    monthly_sales = [0] * 12
    for row in filtered_data:
        month = int(row['date'][5:7])
        seats = int(row['seats'])
        monthly_sales[month - 1] += seats

    return jsonify(monthly_sales)

if __name__ == '__main__':
    app.run()
