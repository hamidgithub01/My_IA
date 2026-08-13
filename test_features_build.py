from ml.features.build import build_feature_dataset


print('\n========== FEATURE DATASET TEST ==========\n')

dataset = build_feature_dataset()

print('Total rows:', len(dataset))

if dataset:

    print('\n========== FIRST FEATURE ROW ==========\n')

    for key, value in dataset[0].items():
        print(f'{key}: {value}')

    print('\n========== FEATURE COUNT ==========\n')
    print('Total features:', len(dataset[0]))

else:

    print('No feature data available.')

    