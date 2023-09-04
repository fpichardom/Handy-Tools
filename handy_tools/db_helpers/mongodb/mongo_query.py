import pymongo
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from typing import List


def get_geolocate_geonames_b1(collection:Collection) -> Cursor:
    """
    Extract summary for geolocate geonames matches with exactly one match best geonames match. This will be considered as bucket 1. (B1)
    """
    pipeline = [
        {
            '$match': {
                'geonames_matches.matches': {
                    '$size': 1
                }
            }
        }, {
            '$unwind': {
                'path': '$geonames_matches.matches', 
                'includeArrayIndex': 'string', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$project': {
                'reference_id': '$data._id', 
                'reference_collection': '$data.collection', 
                'locality_full_normalized': '$data.localityFullNormalized', 
                'inf_lang': '$data.localityInferredLang', 
                'parse_pattern': '$geonames_matches.matches.geolocate_feature.parsePattern', 
                'score': '$geonames_matches.matches.geolocate_feature.score', 
                'precision': '$geonames_matches.matches.geolocate_feature.precision', 
                'x': '$geonames_matches.matches.geolocate_feature.x', 
                'y': '$geonames_matches.matches.geolocate_feature.y', 
                'np_name': '$geonames_matches.matches.np_match.name', 
                'np_fcl': '$geonames_matches.matches.fcl', 
                'np_fcode': '$geonames_matches.matches.np_match.fcode', 
                'adm_name': '$geonames_matches.matches.adm_match.name', 
                'adm_fcl': '$geonames_matches.matches.adm_match.fcl', 
                'adm_fcode': '$geonames_matches.matches.np_match.fcode'
            }
        }
    ]
    return collection.aggregate(pipeline)


def get_union_locality_cluster(locality_collection:Collection) -> Cursor:
    """
    This is used to create the georeferencing collection that merges the localities not in clusters and the clusters.
    """

    cluster_union_pipeline:List = [
        {"$project":
            {
                "localityFullNormalized":"$geoProcessing.localityFullNormalized",
                "localityFullNormalizedAscii": "$geoProcessing.localityFullNormalizedAscii",
                "localityInferredLang": "$geoProcesing.lang",
                "collection": "locality_cluster",
                "country": "USA",
                "state": "Puerto Rico",
                
            }
        }
    ]
    
    locality_pipeline:List = [
        {"$match":
            {
                "isInCluster":False
            }
        },
        {"$project":
            {
                "localityFullNormalized":"$geoProcessing.localityFullNormalized",
                "localityFullNormalizedAscii": "$geoProcessing.localityFullNormalizedAscii",
                "localityInferredLang": "$geoProcesing.lang",
                "collection":"locality",
                "country": "USA",
                "state": "Puerto Rico"
            }
        },
        {
            "$unionWith":
            {
                "coll": "locality_cluster",
                "pipeline": cluster_union_pipeline
            }
        }
        
        
    ]

    return locality_collection.aggregate(locality_pipeline)



def get_geolocate_records_parsing(collection):
    """
    Flattens all the geolocate results from the georeferencing collection extracting only the entries where the geolocation was a success.
    """

    pipeline = [
        {
            '$project': {
                'locality_full_normalized': '$data.localityFullNormalized',
                'locality_full_normalized_ascii': '$data.localityFullNormalizedAscii',
                'reference_id': '$data._id', 
                'reference_collection': '$data.collection', 
                'infer_lang': '$data.localityInferredLang', 
                'geolocate_result': {
                    '$arrayElemAt': [
                        {
                            '$map': {
                                'input': {
                                    '$filter': {
                                        'input': '$geolocateResults',
                                        'cond':{
                                            '$eq':['$$this.success', True]
                                        }
                                    }        
                                },
                                'in': '$$this.geolocateResult'
                            }
                        },#'$geolocateResults.geolocateResult', 0
                        0
                    ]
                }   
                        
            }
        }, {
            '$unwind': {
                'path': '$geolocate_result.features', 
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$addFields': {
                'parse_pattern': '$geolocate_result.features.properties.parsePattern', 
                'score': '$geolocate_result.features.properties.score', 
                'precision': '$geolocate_result.features.properties.precision', 
                'debug': '$geolocate_result.features.properties.debug', 
                'x': {
                    '$first': '$geolocate_result.features.geometry.coordinates'
                }, 
                'y': {
                    '$last': '$geolocate_result.features.geometry.coordinates'
                }, 
                'displaced_dist_miles': '$geolocate_result.features.properties.displacedDistanceMiles', 
                'displaced_head_degrees': '$geolocate_result.features.properties.displacedHeadingDegrees'
            }
        }, {
            '$unset': 'geolocate_result'
        }
    ]
    cursor = collection.aggregate(pipeline)

    return cursor



def process_document(doc, pair_res):
    geonames_matches = {
        "download_uuid": doc["geolocateResults"][0]["downloadHistory"]["download_uuid"],
        "matches": []
    }
    if doc.get("geolocateResults", 0):
        for result in doc["geolocateResults"]:
            if result.get("geolocateResult"):
                for index, feature in enumerate(result["geolocateResult"]["features"]):
                    debug = feature["properties"]["debug"]
                    for res in pair_res:
                        if f"Adm={res['ADM']}" in debug and f"NP={res['NP']}" in debug:
                            
                            match = {
                                "pair_keys":{
                                    "ADM": res['ADM'],
                                    "NP": res['NP'],
                                },
                                "geolocate_feature":{
                                    "index": index,
                                    "parsePattern": feature["properties"]["parsePattern"],
                                    "score": feature["properties"]["score"],
                                    "precision": feature["properties"]["precision"],
                                    "displacedDistanceMiles": feature["properties"]["displacedDistanceMiles"],
                                    "displacedHeadingDegrees":feature["properties"]["displacedHeadingDegrees"],
                                    "debug": debug,
                                    "x": feature["geometry"]["coordinates"][0],
                                    "y": feature["geometry"]["coordinates"][1],
                                
                                },
                                "np_match": res["match_pair"][0],
                                "adm_match": res["match_pair"][1]
                            }
                            
                            geonames_matches["matches"].append(match)
                            break # no need to check other pairs if we found a match
     
        
        if geonames_matches["matches"]:
            return geonames_matches

    return None