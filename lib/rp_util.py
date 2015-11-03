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
