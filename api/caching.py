import json
import datetime

def cache(path: str, data: dict):
    """Save a dictionary (data) to a json file (path)"""
    cached_data = {
        'data': data,
        'last_updated': datetime.datetime.now().timestamp()
    }

    with open(f'cache/{path}', 'w+') as f:
        json.dump(cached_data, f)

def get_cache(path: str, expiration: datetime.timedelta = None, update_function = None, func_args: tuple = ()):
    """Get data from the cache. If there's a defined expiration, run the defined update_function. If one of them isn't defined, the update/expiration will not be checked."""
    cached_data = {}
    
    try:
        with open(f'cache/{path}', 'r+') as f:
            cached_data = json.load(f)
    except:
        # if file doesn't exist/fails to load, get it again
        if hasattr(func_args, '__iter__'):
            data = update_function(*func_args)
        else:
            data = update_function(func_args)

        return data

    if expiration and update_function:
        # if the cache is expired, run the update_function
        if datetime.datetime.now() - expiration > datetime.datetime.fromtimestamp(cached_data['last_updated']):
            #print('out of date')
            try:
                if hasattr(func_args, '__iter__'):
                    data = update_function(*func_args)
                else:
                    data = update_function(func_args)

                return data
            except:
                print('cache update failed!')
                # out of date but update failed for some reason, just return the current data
                pass


    return cached_data['data']