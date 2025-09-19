from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import pandas as pd
from .models import Connection, Auth0User, Chat, Message
import json

"""def run_sql_query(connection_url, sql_query, context=None):
    DATABASE_URL = connection_url
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    sql_query = text(sql_query)
    print(sql_query)
    result = session.execute(sql_query)

    #with engine.begin() as connection:
    #    result = connection.execute(sql_query)
    #    print(result.rowcount) 
    
    # in this case, we can use the following operators 
    # on result to print the text the execute returns:
    #result.fetchall()
    engine.dispose()
    
    return result"""

"""def run_sql_query(connection_url, sql_query, context=None):
    DATABASE_URL = connection_url
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    sql_query = text(sql_query)
    print(sql_query)
    
    try:
        result = session.execute(sql_query)
        result.keys()
        return result

    except:
        print("except... :()")
        result = None
        

    with engine.begin() as connection:
        result = connection.execute(sql_query)
        affected_rows = result.rowcount
        print(affected_rows)

    engine.dispose()
    
    return result"""

def run_sql_query(connection_url, sql_query, context=None):
    engine = create_engine(connection_url, echo=True)
    sql_query = text(sql_query)

    try:
        with engine.begin() as connection:
            result = connection.execute(sql_query)
            print('results++++++++++++++++++++++++++++++=')
            print(result)
            try:
                affected_rows = result.rowcount
                print(affected_rows)
                columns = result.keys()
                data = result.fetchall()

            except:
                return{"success": True, "affected_rows": affected_rows, "response_data": None}
            
            # Convert the result to a pandas DataFrame
            df = pd.DataFrame(data, columns=columns)
            response_data = df.head(5).to_json(orient='records')
            print(df)
            
            return {"affected_rows": affected_rows, "response_data": response_data}
        
    except Exception as e:
        print("An error occurred:", e)
        return {"error": True, "affected_rows": str(e), "response_data": None}
    finally:
        engine.dispose()

def get_db_schema(connection_url, context=None):
    DATABASE_URL = connection_url
    try:
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        inspector = inspect(engine)
        db_metadata = {}

        for table_name in inspector.get_table_names():
            
            columns = {}
            for column in inspector.get_columns(table_name):
                columns[column["name"]] = {"type": column["type"]}

            relationships = {}
            for fk in inspector.get_foreign_keys(table_name):
                relationships[fk["referred_table"]] = {
                    "local_column": fk["constrained_columns"][0],
                    "remote_column": fk["referred_columns"][0],
                }

            db_metadata[table_name] = {"columns": columns, "relationships": relationships}
        print("db_metadata: ")
        # print(db_metadata)
        # close connection
        #engine.dispose()
        return db_metadata
    except Exception as e:
        print(e)
        return None