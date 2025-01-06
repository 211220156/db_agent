from helper_func import *

agent = create_csv_agent(data_path="./data/data.csv", debug=True)

# agent = create_sql_agent(
#     host="127.0.0.1",
#     user="root",
#     password="root",
#     database="demo",
#     debug=True
# )

run_loop(agent)