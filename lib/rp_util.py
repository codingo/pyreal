from random import randint

def get_random_id(max_id):
  """
  return a id randomly between 0 and max_id
  """
  return randint(0,max_id)

def int2dollar(num):
  """
  convert a integer to dollar format like $xx,xxx,xxx
  """
  str_num = str(num)
  str_len = len(str_num)
  
  if str_len <= 3:
    return '$' + str_num
  else:
    count = 1
    result = []
    right_len = str_len % 3
    right_part = '$' + str_num[0:right_len]
    result.append(right_part)
    
    for i in range(1,((str_len - right_len) / 3) + 1 ):
        result.append(str_num[right_len*i:right_len*i + 3])
        count = count + 1
    return ','.join(result)
    
def dollar2int(str_dollar):
  """
  convert a dollar format string to a integer
  """
  return int(str_dollar.replace('$','').replace(',',''))

def get_total_num(in_str):
    """
    extract the page number from below string
    Showing 1 - 20 of 54 total results
    """
    pos_total = in_str.index('total')
    pos_of = in_str.index('of')
    return int(in_str[pos_of + 2:pos_total].strip())

def get_max_page(int_total_property):
    """
    return the max page based on total number property
    """
    per_page = 20
    if int_total_property <= 20:
        return 1
    else:
        return (int_total_property - (int_total_property % per_page)) / per_page + 1

def replace_page_num(start_url, page_num):
    """
    http://www.realestate.com.au/sold/in-karama+nt+812/list-1?activeSort=solddate&includeSurrounding=false
    replace the list-1 to list-n, n is page_num
    """
    first_part = start_url[0:start_url.index('list')]
    second_part = start_url[start_url.index('?'):]
    return first_part + 'list-' + str(page_num) + second_part
