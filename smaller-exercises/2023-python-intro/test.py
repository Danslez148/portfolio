def merge(list1,list2):
    new_list = []
    while len(list1)>0 and len(list2)>0:
        if list1[0] > list2[0]:
            new_list.append(list2[0])
            del list2[0]
        else:
            new_list.append(list1[0])
            del list1[0]
    return new_list+list1+list2

def merge_sort(values):
    if len(values)>1:
        sorted1 = merge_sort(values[:len(values)//2])
        sorted2 = merge_sort(values[len(values)//2:])
        return merge(sorted1,sorted2)
    else:
        return values
    
values = [2, 5, 3, 1, 7, 4, 0, 9]
n_list = merge_sort(values)
print(n_list)