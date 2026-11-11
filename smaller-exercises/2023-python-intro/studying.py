def swap(values, source, dest):
    values[source], values[dest] = values[dest], values[source]
    
def partition(values, start, stop):
    pivot = values[stop]
    midpoint = start
    for position in range(start, stop):
        if values[position] <= pivot:
            swap(values, position, midpoint)
            midpoint += 1
        swap(values, midpoint, stop)
        return midpoint

def quick_sort2(values,start,stop):
    if stop > start:
        pivot = partition(values,start,stop)
        quick_sort2(values,start,pivot-1)
        quick_sort2(values,pivot+1,stop)
        
def quick_sort(values):
    quick_sort2(values,0,len(values)-1)
    return values

inlist = [0, 7, 8, 10, 3, 5, 2, 17]
print(quick_sort(inlist))
    