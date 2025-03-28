import re


def url_to_html(match):
        url = match.group(0)
        if re.search(r'\.(png|jpg|jpeg|gif|bmp|webp)$', url, re.IGNORECASE):
            return f'<img style="max-width: 200px; max-height: 200px;" src="{url}" alt="{url}">'
        else:
            return f'<a href="{url}">{url}</a>'
    
def format_content(content:str):
    content = content.replace("&", "&amp;")
    content = content.replace(">", "&gt;")
    content = content.replace("<", "&lt;")
    content = content.replace("  ", " &nbsp;")
    content = content.replace("\n", "<br>")
    content = re.sub(r'##(.*?)##', r'<strong>\1</strong>', content)
    content = re.sub(r'@(\w+)', "<a href='user_name/" + r'\1' + "'>@" + r'\1' + "</a>", content)
    content = re.sub(r'https?://[a-zA-Z0-9\-._~:/?#[\]@!$&\'()*+,;=.]+', url_to_html, content)
    
    return content