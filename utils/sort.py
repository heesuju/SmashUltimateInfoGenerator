
def sort_by_priority(mods, priority:list):
    sorted_data = sorted(mods, key=lambda x: (x[priority[0]], x[priority[1]], x[priority[2]], x[priority[3]]), reverse=False)
    return sorted_data