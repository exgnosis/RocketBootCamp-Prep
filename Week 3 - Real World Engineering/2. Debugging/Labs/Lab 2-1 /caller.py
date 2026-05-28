from mean_fixed import mean

datasets = [
    [4, 5, 6],
    [10, 20, 30, 40],
    [],
    [3.5, 7.5],
]

for data in datasets:
    try:
        result = mean(data)
        print(f"mean({data}) = {result}")
    except ValueError as e:
        print(f"mean({data}) skipped: {e}")
