import requests

def search_geonames_q(q,country, username, fuzzy=1):
    # URL without the query parameters
    url = 'http://api.geonames.org/searchJSON'

    # dictionary of query parameters
    params = {
        'q': q,
        'maxRows': 10,
        'username': username,  # replace 'username' with your actual GeoNames username
        'country': country,
        'fuzzy':fuzzy,
    }


    # send a GET request to the URL with the query parameters
    response = requests.get(url, params=params)

    # check if the request was successful
    if response.status_code == 200:
        # parse the JSON response into a dictionary
        data = response.json()
        # return the data
        return data
    else:
        print(f'Request failed with status code {response.status_code}')
        return None

def search_geonames_name(name,country, username, fuzzy=1):
    # URL without the query parameters
    url = 'http://api.geonames.org/searchJSON'

    if isinstance(name, str):
        if len(name) > 0:
            # dictionary of query parameters
            params = {
                'q': name,
                'maxRows': 10,
                'username': username,  # replace 'username' with your actual GeoNames username
                'country': country,
                'fuzzy':fuzzy,
                'orderby': 'relevance',
                'isNameRequired': 'true',
                'name_startsWith': name[0]
            }

            # send a GET request to the URL with the query parameters
            response = requests.get(url, params=params)

            # check if the request was successful
            if response.status_code == 200:
                # parse the JSON response into a dictionary
                data = response.json()
                # return the data
                return data
            else:
                print(f'Request failed with status code {response.status_code}')       
                return None
        else:
            print("Name is empty")
            print(name)
            return None
    else:
        print("Name is not a string")
        return None

def search_geonames_admin(name, country, username):
    # URL without the query parameters
    url = 'http://api.geonames.org/searchJSON'

    if isinstance(name, str):
        if len(name) > 0:

            # dictionary of query parameters
            params = {
                'q': name,
                'maxRows': 10,
                'username': username,  # replace 'username' with your actual GeoNames username
                'country': country,
                'featureClass': 'A',
                'fuzzy':1,
                'orderby': 'relevance',
                'isNameRequired': 'true',
                'name_startsWith': name[0]
            }

            # send a GET request to the URL with the query parameters
            response = requests.get(url, params=params)

            # check if the request was successful
            if response.status_code == 200:
                # parse the JSON response into a dictionary
                data = response.json()
                # return the data
                return data
            else:
                print(f'Request failed with status code {response.status_code}')
                return None
            
        else:
            print("Name is empty")
            print(name)
            return None
    else:
        print("Name is not a string")
        return None 
    

def search_geonames_np_adm_pairs(pair_list, two_letter_country, geonames_username):
    #pair_results = []
    formatted_pair_res = []
    rerun_pair_list = []
    current_pair_index = 0
    
    for index, pair in enumerate(pair_list):
        current_pair_index = index
        try:
            np_res = search_geonames_name(pair[0],two_letter_country, geonames_username)
            adm_res = search_geonames_admin(pair[1], two_letter_country, geonames_username)
            if np_res is not None and adm_res is not None:
                if 'status' not in np_res and 'status' not in adm_res:
                    print

                    res = {
                        'NP': pair[0],
                        'ADM': pair[1],
                        'geonamesNP': np_res,
                        'geonamesADM': adm_res
                    }

                    formatted_pair_res.append(res)
                else:
                    rerun_pair_list.append(pair)


            #pair_results.append((np_res,adm_res))
    
        except Exception as e:
            print(f"Error in search_geonames_np_adm_pairs: {pair}|index: {current_pair_index}")
            print(e)
            continue
    return formatted_pair_res, rerun_pair_list  


def extract_items(lst, indexes):
    extracted_items = [lst[1] for i in indexes]
    return extracted_items