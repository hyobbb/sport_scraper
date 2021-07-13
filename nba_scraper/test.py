def parse_url(value:str):
    value = value.replace('//', 'https://')
    return value


url = parse_url('//www.nba.com/some/')
print(url)