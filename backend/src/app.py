from flask import Flask, request
from flask_cors import CORS

from src.modules import process_data as pr
from src.modules import web_scraper as ws

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/process', methods=['POST', 'OPTIONS'])
def process():
    if request.method == 'OPTIONS':
        return {}, 200
    try:
        
        try:
            data = request.get_json()
            strike = int(data['strike'])
            tmax_trigger = int(data['triggerTmax'])
            start_year = int(data['startYear'])
        except Exception as e:
            print(f"Bad request: {e}")
            return {'success': False}, 400

        annual_payout, daily_payout = pr.calculate_payout(strike, tmax_trigger, start_year)

        print('backend hit successfully')

        return {
            'success': True,
            'annualChartData': annual_payout,
            'dailyChartData': daily_payout
            }, 200
    except Exception as e:
        print(f"Exception: {e}")
        return {'success': False}, 500
    

@app.route('/future', methods=['GET'])
def future():
    try:
        future = ws.get_future(timeout=20)
        return {
            'success': True,
            'future': future
            }, 200
    except Exception as e:
        print(f'Unable to get future: {e}')
        return {
            'success': False
        }, 500


if __name__ == '__main__':
    app.run()