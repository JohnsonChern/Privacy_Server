import json

type_error = -1

def merge_array(base, head):

	if type(base) != list or type(head) != list:
		return type_error

	result = base
	for item in head:
		if item in base:
			continue
		else:
			if type(item) not in [list, dict]:
				result.append(item)
			else:
				index = None
				for new_base in base:
					if type(new_base) == type(item):
						index = base.index(new_base)
						break
				if index is None:
					result.append(item)
					continue
				if type(new_base) is list:
					result[index] = merge_array(new_base, item)
				elif type(new_base) is dict:
					result[index] = merger(new_base, item)

	return sorted(result)
			

def merger(base, head):

	if not isinstance(base, dict) or not isinstance(head, dict):
		return type_error

	result = base
	for key in head:
		if key not in base:
			result[key] = head[key]
		elif type(head[key]) not in [list, dict]:
			result[key] = head[key]
		elif type(head[key]) is list:
			result[key] = merge_array(result[key], head[key])
		elif type(head[key]) is dict:
			result[key] = merger(result[key], head[key])

	return result
