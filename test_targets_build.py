from ml.targets.build import build_target_dataset


print()
print('========== TARGET DATASET TEST ==========')
print()

dataset = build_target_dataset()

print(
    f'Total rows: {len(dataset)}'
)

if dataset:

    print()
    print('========== FIRST TARGET ROW ==========')
    print()

    for key, value in dataset[0].items():

        print(
            f'{key}: {value}'
        )

    print()
    print('========== TARGET COUNT ==========')
    print()

    print(
        f'Total targets: '
        f'{len(dataset[0]) - 1}'
    )

else:

    print()
    print('No target data available.')