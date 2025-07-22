"""Utility functions for Jira API Extractor."""

def parse_adf_to_text(adf):
    """Parses an Atlassian Document Format object into a plain text string."""
    if not isinstance(adf, dict) or 'content' not in adf:
        # If it's not a valid ADF object, return it as is (might be a simple string).
        return str(adf)

    text_content = []
    for block in adf.get('content', []):
        if block.get('type') == 'paragraph':
            for item in block.get('content', []):
                if item.get('type') == 'text':
                    text_content.append(item.get('text', ''))
    return " ".join(text_content)

def paginate_request(session, url, headers, params, auth, max_results_key='maxResults', start_at_key='startAt'):
    """
    Generic pagination handler for Jira API requests.
    
    Args:
        session: requests session object
        url: API endpoint URL
        headers: request headers
        params: request parameters
        auth: authentication tuple
        max_results_key: parameter name for max results per page
        start_at_key: parameter name for pagination offset
    
    Returns:
        List of all results from paginated requests
    """
    all_results = []
    start_at = 0
    max_results = 100  # Default page size
    
    # Set initial pagination parameters
    params = params.copy()
    params[max_results_key] = max_results
    
    while True:
        params[start_at_key] = start_at
        
        try:
            response = session.get(url, headers=headers, params=params, auth=auth)
            response.raise_for_status()
            data = response.json()
            
            # Handle different response structures
            if 'issues' in data:
                results = data['issues']
                total = data.get('total', 0)
            elif 'values' in data:
                results = data['values']
                total = data.get('total', 0)
            else:
                # Fallback for other response structures
                results = data if isinstance(data, list) else [data]
                total = len(results)
            
            all_results.extend(results)
            
            # Check if we've retrieved all results
            if len(results) < max_results or start_at + len(results) >= total:
                break
                
            start_at += len(results)
            
        except Exception as e:
            print(f"Error during pagination at offset {start_at}: {str(e)}")
            break
    
    return all_results
