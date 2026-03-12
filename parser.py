from bs4 import BeautifulSoup
import re

def parse_post_html(html_content, keywords):
    """
    Parses a single LinkedIn post HTML and extracts data.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    post_data = {
        'post_url': '',
        'author_name': '',
        'author_profile_url': '',
        'post_text': '',
        'date_posted': '',
        'likes': 0,
        'comments': 0,
        'reposts': 0,
        'matched_keywords': [],
        'post_type': 'original'
    }
    
    # 1. Author Name & Profile URL
    author_elem = soup.find('a', class_=re.compile(r'update-components-actor__meta-link'))
    if author_elem:
        post_data['author_profile_url'] = author_elem.get('href', '').split('?')[0]
        name_elem = author_elem.find('span', dir='ltr')
        if name_elem:
            post_data['author_name'] = name_elem.get_text(strip=True)
            
    # 2. Post Text
    text_elem = soup.find('div', class_=re.compile(r'update-components-text'))
    if text_elem:
        post_data['post_text'] = text_elem.get_text(separator='\n', strip=True)
        
    # 3. Post URL
    urn_elem = soup.find('div', {'data-urn': True})
    urn = urn_elem.get('data-urn') if urn_elem else None
    
    # Sometimes LinkedIn hides the data-urn on a different wrapper element
    if not urn:
        for div in soup.find_all('div'):
            if div.get('data-urn'):
                urn = div.get('data-urn')
                break

    if urn:
        post_data['post_url'] = f"https://www.linkedin.com/feed/update/{urn}/"
    else:
        # Fallback to search links inside the post if URN is completely missing
        link = soup.find('a', href=re.compile(r'/feed/update/urn:li:activity'))
        if link:
            post_data['post_url'] = link.get('href', '').split('?')[0]
        
    # 4. Date Posted
    date_elem = soup.find('span', class_=re.compile(r'update-components-actor__sub-description'))
    if date_elem:
        date_text = date_elem.get_text(strip=True).replace('•', '').strip()
        # Clean up: take only the first token before spaces or "Visible to anyone"
        import re as re_mod
        match = re_mod.search(r'^([^\s]+)', date_text)
        if match:
            post_data['date_posted'] = match.group(1)
        else:
            post_data['date_posted'] = date_text
        
    # 5. Engagement (Likes, Comments, Reposts)
    likes_elem = soup.find('span', class_=re.compile(r'social-details-social-counts__reactions-count'))
    if likes_elem:
        likes_text = likes_elem.get_text(strip=True).replace(',', '')
        post_data['likes'] = int(likes_text) if likes_text.isdigit() else 0
        
    comments_elem = soup.find('button', attrs={'aria-label': re.compile(r'comment', re.I)})
    if comments_elem:
        comment_text = comments_elem.get_text(strip=True)
        num = re.search(r'(\d+)', comment_text.replace(',', ''))
        if num:
            post_data['comments'] = int(num.group(1))

    reposts_elem = soup.find('button', attrs={'aria-label': re.compile(r'repost', re.I)})
    if reposts_elem:
        repost_text = reposts_elem.get_text(strip=True)
        num = re.search(r'(\d+)', repost_text.replace(',', ''))
        if num:
            post_data['reposts'] = int(num.group(1))
            
    # 6. Matched Keywords
    text_lower = str(post_data['post_text']).lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            if isinstance(post_data['matched_keywords'], list):
                post_data['matched_keywords'].append(kw)
            
    # 7. Post Type
    header_elem = soup.find('span', class_=re.compile(r'update-components-header__text-view'))
    if header_elem and 'reposted' in header_elem.get_text(strip=True).lower():
        post_data['post_type'] = 'repost'
    elif 'article' in str(post_data['post_url']).lower():
        post_data['post_type'] = 'article'

    return post_data
