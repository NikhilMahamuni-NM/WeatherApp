
def get_avg(value_list):
    value = round(sum(value_list)/len(value_list),1)

    return value


def get_max_occurring_value(value_list: list):
    value = max(value_list,key=value_list.count)

    return value