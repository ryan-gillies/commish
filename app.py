from flask import Flask, render_template, jsonify
from pools.pool import Pool

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Define API endpoint to fetch leaderboard data
# @app.route('/leaderboard/<pool_class>')
# def get_leaderboard(pool_class):
#     # Fetch leaderboard data based on pool class
#     leaderboard_data = Pool.get_leaderboard(pool_class)
#     return jsonify(leaderboard_data)


# @app.route('/leaderboards.html')
# def leaderboards():
#     season = league.get_season(league.state)
#     seasons = list(range(2023,season+1))
#     seasons.sort(reverse=True)
#     leaderboard_small_scoring_margin = Pool.PoolFactory.create_pool()
#     return render_template('leaderboards.html', seasons=seasons, leaderboard_small_scoring_margin=leaderboard_small_scoring_margin)

if __name__ == '__main__':
    app.run(debug=True)


