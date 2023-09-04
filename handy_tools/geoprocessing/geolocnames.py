from .similarity import levenshtein_similarity

def max_indices(lst):
    max_value = max(lst)
    return [i for i, v in enumerate(lst) if v == max_value]


def filter_geonames_pairs(pair):

    # Set default values
    filtered_adm = []
    filtered_np = []
    result = {
        'ADM': pair['ADM'],
        'NP': pair['NP'],
        'reference_id': pair['_id'],
        'match_pair_len': 0,
        'match_pair': pair           
    }  # Default result

    # Check existence of 'geonamesADM' and 'totalResultsCount'
    if not pair.get('geonamesADM') or 'totalResultsCount' not in pair['geonamesADM']:
        return result
    
    # Filter ADM for later comparison to NP
    if pair['geonamesADM']['totalResultsCount'] > 0:
        adm_res =  pair['geonamesADM']['geonames']
        similarity_scores_adm = [float(levenshtein_similarity(res['name'],pair['ADM'])) for res in adm_res]
        hi_sim_adm = max_indices(similarity_scores_adm)
        filtered_adm = [adm_res[i] for i in hi_sim_adm]
    else:
        return result

    # Check existence of 'geonamesNP' and 'totalResultsCount'
    if not pair.get('geonamesNP') or 'totalResultsCount' not in pair['geonamesNP']:
        return result
    
    if pair['geonamesNP']['totalResultsCount'] > 0:
        np_res =  pair['geonamesNP']['geonames']
        similarity_scores_np = [float(levenshtein_similarity(res['name'],pair['NP'])) for res in np_res]
        hi_sim_np = max_indices(similarity_scores_np)
        filtered_np = [np_res[i] for i in hi_sim_np]
    else:
        return result

    # Number of pairs equal to 
    np_adm_pair_matches = []

    # Make sure that there is a match between the best options of admin and np
    for adm in filtered_adm:
        np_admin_match = [np for np in filtered_np if np['adminName1'] == adm['adminName1']]
        np_adm_pair_matches.append((np_admin_match, adm))
    
    # Test if there is a single match for administrative area and check if for that single match there is also a single best match of named place
    if len(np_adm_pair_matches) == 1 and len(np_adm_pair_matches[0][0]) == 1:

        result['match_pair_len'] = 1
        result['match_pair'] = [np_adm_pair_matches[0][0][0],np_adm_pair_matches[0][1]]

        return result
        #return {
        #    "match_pair_len":1,
        #    "match_pair":[np_adm_pair_matches[0][0],np_adm_pair_matches[0][1]]
        #}

    result['match_pair_len'] = 2
    result['match_pair'] = np_adm_pair_matches

    return result
    #return {
    #    "match_pair_len":2,
    #    "match_pair": np_adm_pair_matches
    #}