from llm import LargeLanguageModel
from aserious_agent.pandas_agent import create_pandas_dataframe_agent
from langchain.globals import set_verbose
from pymongo import MongoClient

import pandas as pd

import datetime
import pytz
import yaml
import fastapi
import uvicorn

# set_verbose(True)
# app = fastapi.FastAPI()

# client = MongoClient('quincy.lim-everest.nord', port=27017, username='', password='27017')
# # db = client['logs']
# # collection = db['de-carton']

# with open('./model_configs/neural-chat.yml', 'r') as f:
#     model_config = yaml.safe_load(f)

# with open('./prompts/pandas_prompt_04.yml', 'r') as f:
#     prompt_config = yaml.safe_load(f)

# llm = LargeLanguageModel(**model_config, **prompt_config)




# # dataframe_agent = create_pandas_dataframe_agent(
# #     llm.llm, 
# #     df,
# #     verbose=True,
# #     prefix=llm.prefix,
# #     suffix=llm.suffix,
# #     input_variables=['input', 'agent_scratchpad', 'df_head'],
# #     agent_executor_kwargs={'handle_parsing_errors': True},
# #     include_df_in_prompt=True,
# #     return_intermediate_steps=True,
# #     max_iterations=10,
# #     max_execution_time=600,
# #     early_stopping_method='force', 
# # )

# # @app.post('/chat')
# # async def chat(msg):
# #     result = dataframe_agent({'input': msg})
# #     collection.insert_one({
# #         'datetime': datetime.datetime.now(pytz.timezone('Asia/Singapore')),
# #         'query': msg,
# #         'output': result.get('output')
# #     })

# #     return result.get('output')


# # @app.post("/chat")
# # async def chat2(user_query: str, database_name: str):

# #     # Get the collection
# #     db = client[database_name]

# #     # Convert the collection to a DataFrame
# #     data = pd.DataFrame(list(db.find()))

# #     print(data)
# #     result = chatmsg(user_query,data)
# #     return result


#     # result = dataframe_agent({'input': user_query})

#     # Process the user query on the DataFrame 'data'
#     # This is where you would add your logic to process the user query
#     # For this example, let's assume the user query is a column name and we return its unique values
    
#     # return {"result": result}

# @app.post('/store')
# async def store(path):
#     df = pd.read_csv(path)
#     data_dict = df.to_dict("records")
#     with MongoClient('quincy.lim-everest.nord', port=27017, username='', password='27017',connect=False) as client:
#         db = client.de_carton_test
#         collection = db.sales1_report
#         result = collection.insert_many(data_dict)

# @app.post('/test')
# async def chatmsg(msg,database_name, collection):

#     # Get the collection
#     db = client[database_name]

#     collection = db[collection]

#     # Convert the collection to a DataFrame
#     data = pd.DataFrame(list(collection.find()))

#     dataframe_agent = create_pandas_dataframe_agent(
#     llm.llm, 
#     data,
#     verbose=True,
#     prefix=llm.prefix,
#     suffix=llm.suffix,
#     input_variables=['input', 'agent_scratchpad', 'df_head'],
#     agent_executor_kwargs={'handle_parsing_errors': True},
#     include_df_in_prompt=True,
#     return_intermediate_steps=True,
#     max_iterations=10,
#     max_execution_time=600,
#     early_stopping_method='force', 
#     )

    # evaluator_db = client['logs']

    # evaluator_collection = evaluator_db['de-carton']
    
    # result = dataframe_agent({'input': msg})
    # evaluator_collection.insert_one({
    #     'datetime': datetime.datetime.now(pytz.timezone('Asia/Singapore')),
    #     'query': msg,
    #     'output': result.get('output')
    # })

#     return result.get('output')



# if __name__ == "__main__":
#     uvicorn.run('main:app', host="0.0.0.0", port=8082, reload=False)




# main.py
from LLM import LargeLanguageModelAgent
from MongoDB import MongoDBOperations
from langchain.globals import set_verbose
import fastapi
import uvicorn
import pandas as pd

set_verbose(True)
app = fastapi.FastAPI()

llm_agent = LargeLanguageModelAgent('./model_configs/neural-chat.yml', './prompts/pandas_prompt_04.yml')
mongo_ops = MongoDBOperations('quincy.lim-everest.nord', 27017, '', '27017')

@app.post('/store')
async def store(companyName, csv_file):
    df = pd.read_csv(f"./data/csv_data/{csv_file}.csv")
    data_dict = df.to_dict("records")
    mongo_ops.insert_many(companyName, csv_file, data_dict)

@app.post('/chat')
async def chatmsg(msg, database_name, collection):
    data = mongo_ops.find_all(database_name, collection)
    dataframe_agent = llm_agent.create_dataframe_agent(data)
    result = dataframe_agent({'input': msg})

    #evaluation table
    mongo_ops.insert_many('logs', 'de-carton', {
        'datetime': datetime.datetime.now(pytz.timezone('Asia/Singapore')),
        'query': msg,
        'output': result.get('output')
    })
    return result.get('output')

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8082, reload=False)
