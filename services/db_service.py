from services.login_service import init_connection

client = init_connection()

def getData(*, table, selector):
    try:
        response = client.table(table).select(selector).execute()
        return response
    except Exception as e:
        return e

def getDataWhere(*, table, selector, condition, value):
    try:
        response = client.table(table).select(selector).eq(condition, value).execute()
        return response.data if hasattr(response, 'data') else []
    except Exception as e:
        return e
    
def insertData(*, table, data):
    try:
        response = client.table(table).insert(data).execute()
        return response
    except Exception as e:
        return e

def updateData(*, table, data, condition, value):
    try:
        response = client.table(table).update(data).eq(condition, value).execute()
        return response
    except Exception as e:
        return e
    
def deleteData(*, table, condition, value):
    try:
        response = client.table(table).delete().eq(condition, value).execute()
        return response
    except Exception as e:
        return e