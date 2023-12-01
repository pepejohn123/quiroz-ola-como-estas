#!/usr/bin/env python3
import datetime
import json

import pydgraph


def set_schema(client):
    schema = """
    type Airline {
        name
        schedules
    }

    type Flight {
        ID
        wait
    }


    name: string .
    schedules: [uid] .

    ID: int .
    wait: int @index(int). 
    """
    return client.alter(pydgraph.Operation(schema=schema))


def create_data(client, jsonpath):
    # Create a new transaction.
    txn = client.txn()
    json_file_path = jsonpath
    with open(json_file_path, 'r') as json_file:
    # Load the JSON content into a list of dictionaries
        data = json.load(json_file)
    
    try:
        p = data
        response = txn.mutate(set_obj=p)

        # Commit transaction.

        commit_response = txn.commit()
        print(f"Commit Response: {commit_response}")

        print(f"UIDs: {response.uids}")
    finally:
        # Clean up.
        # Calling this after txn.commit() is a no-op and hence safe.
        txn.discard()


def delete_artist_song(client, name):
    # Create a new transaction.
    txn = client.txn()
    try:
        query1 = """query search_artist_song($a: string) {
            all(func: eq(name, $a)) {
               uid
            }
        }"""
        variables1 = {'$a': name}
        res1 = client.txn(read_only=True).query(query1, variables=variables1)
        deleted_object = json.loads(res1.json)
        for object in deleted_object['all']:
            print("UID: " + object['uid'])
            txn.mutate(del_obj=object)
            print(f"{name} deleted")
        commit_response = txn.commit()
        print(commit_response)
    finally:
        txn.discard()



def fastest_airlines(client):
    query = """{
  avg_wait as var(func: type(Airline), orderdesc: name){ {
      name
      schedules {
        longest as wait    
      }
    total as avg(val(longest))  
    }
  }
        
fastest(func: uid(avg_wait) ,orderasc: val(total), first: 5) {
    name
    total : val(total)
 	 }
}"""

    res = client.txn(read_only=True).query(query)
    airlines = json.loads(res.json)

    # Print results.
    print(f"Data associated with fastest airlines:\n{json.dumps(airlines, indent=2)}")


def slowest_airlines(client):
    query = """{
  avg_wait as var(func: type(Airline), orderdesc: name){ {
      name
      schedules {
        longest as wait    
      }
    total as avg(val(longest))  
    }
  }
        
slowest(func: uid(avg_wait) ,orderdesc: val(total), first: 5) {
    name
    total : val(total)
 	 }
}"""

    res = client.txn(read_only=True).query(query)
    airlines = json.loads(res.json)

    # Print results.
    print(f"Data associated with slowest airlines:\n{json.dumps(airlines, indent=2)}")

def drop_all(client):
    return client.alter(pydgraph.Operation(drop_all=True))
