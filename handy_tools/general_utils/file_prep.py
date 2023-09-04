import re


def parse_herb_filename(filename):
    # Extract institution name, document type, and institution relationship type
    match = re.match(r'^(.+?) (herbarium|org|infp) (annual report|strategic plan|webpage)', filename)
    if match:

        institution_info= {
            'institution_name_original': match.group(1).strip(),
            'institution_name_coded': f'{match.group(1).strip().lower().replace(" ", "_")}',
            
        }

        document_info = {
            'institution_document_relationship': match.group(2).strip(),
            'document_type': match.group(3).strip(),
            'file_format': filename.split(".")[-1].strip(),
            'document_name_original': filename,
        }

        # Create document_name_coded after document_info is fully defined
        document_info['document_name_coded'] = f'{institution_info["institution_name_coded"]}-{document_info["document_type"].lower().replace(" ", "_")}-{document_info["institution_document_relationship"].lower()}'

        return institution_info, document_info
    else:
        return None, None # Make sure to return a pair of None values


def parse_file_name(filename):
    # Extract institution name, document type, and institution relationship type
    match = re.match(r'^(.+?) (annual report|strategic plan|webpage) (pare|bioc|infp)', filename)
    if match:

        institution_info= {
            'institution_name_original': match.group(1).strip(),
            'institution_name_coded': f'{match.group(1).strip().lower().replace(" ", "_")}',
            
        }

        document_info = {
            'institution_document_relationship': match.group(3).strip(),
            'document_type': match.group(2).strip(),
            'file_format': filename.split(".")[-1].strip(),
            'document_name_original': filename,
        }

        # Create document_name_coded after document_info is fully defined
        document_info['document_name_coded'] = f'{institution_info["institution_name_coded"]}-{document_info["document_type"].lower().replace(" ", "_")}-{document_info["institution_document_relationship"].lower()}'

        return institution_info, document_info
    else:
        return None, None # Make sure to return a pair of None values