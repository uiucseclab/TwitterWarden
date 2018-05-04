import csv
import downloadTools
import json
from tqdm import tqdm
import numpy as np
import os
from extractFeatures import getAllFeatures
from twython.exceptions import TwythonAuthError
from sklearn.ensemble import RandomForestClassifier
from random import shuffle

NUM_SUBJECTS = 150
NUM_SLICES = 10

bots = []
people = []

with open('varol-2017.dat','rb') as tsvin:
    for line in tsvin:
        data = line.split()
        if int(data[1]) == 0:
            people.append(data[0])
        else:
            bots.append(data[0])

test_people = np.random.choice(people, NUM_SUBJECTS, replace=False)
test_bots = np.random.choice(bots, NUM_SUBJECTS, replace=False)

people_users = downloadTools.get_users(test_people, 2, False)
bot_users = downloadTools.get_users(test_bots, 2, False)

with open('real_people.json', 'w') as people_out:
    json.dump(people_users, people_out)

with open('bot_people.json', 'w') as bots_out:
    json.dump(bot_users, bots_out)

# people_users = []
# bot_users = []

# with open('real_people.json', 'r') as people_in:
#     people_users = json.load(people_in)

# with open('bot_people.json', 'r') as bots_in:
#     bot_users = json.load(bots_in)

features = []
decisions = []

print "Getting data for real people..."
for person in tqdm(people_users):
    temp_out = dict()
    if os.path.exists('real_data/data_for_realperson_' + person['screen_name'] + '.json'):
        with open('real_data/data_for_realperson_' + person['screen_name'] + '.json', 'r') as fp:
            temp_out = json.load(fp)
    else:
        temp_out['user'] = person
        try:
            temp_out['tweets'] = downloadTools.get_timeline(person['id_str'], 300, 3)
            friends, followers = downloadTools.get_users_around(person['screen_name'], 150, 150, 2)
            temp_out['friends'] = friends
            temp_out['followers'] = followers
        except TwythonAuthError as e:
            continue
        
        with open('real_data/data_for_realperson_' + person['screen_name'] + '.json', 'w') as fp:
            json.dump(temp_out, fp)

    features.append(getAllFeatures(temp_out['user'], temp_out['tweets'], temp_out['friends'], temp_out['followers']))
    decisions.append(0)

print "Getting data for bot people..."
for bot in tqdm(bot_users):
    temp_out = dict()
    if os.path.exists('bot_data/data_for_botperson_' + bot['screen_name'] + '.json'):
        with open('bot_data/data_for_botperson_' + bot['screen_name'] + '.json', 'r') as fp:
            temp_out = json.load(fp)
    else:
        temp_out['user'] = bot
        try:
            temp_out['tweets'] = downloadTools.get_timeline(bot['id_str'], 300, 3)
            friends, followers = downloadTools.get_users_around(bot['screen_name'], 150, 150, 2)
            temp_out['friends'] = friends
            temp_out['followers'] = followers
        except TwythonAuthError as e:
            continue
        
        with open('bot_data/data_for_botperson_' + bot['screen_name'] + '.json', 'w') as fp:
            json.dump(temp_out, fp)

    features.append(getAllFeatures(temp_out['user'], temp_out['tweets'], temp_out['friends'], temp_out['followers']))
    decisions.append(1)

with open('features.csv', 'w') as fp:
    csvWriter = csv.writer(fp, delimiter=',')
    csvWriter.writerows(features)

data = zip(features, decisions)
shuffle(data)
total = len(data)
fold_size = total / NUM_SLICES

fps = [0 for i in range(NUM_SLICES)]
fns = [0 for i in range(NUM_SLICES)]
tps = [0 for i in range(NUM_SLICES)]
tns = [0 for i in range(NUM_SLICES)]

for i in range(NUM_SLICES):
    curr_training = data[:i * fold_size] + data[(i + 1) * fold_size:]
    curr_testing = data[i * fold_size:(i + 1) * fold_size]

    curr_x_train = [x for x,y in curr_training]
    curr_y_train = [y for x,y in curr_training]

    forest = RandomForestClassifier()
    forest.fit(curr_x_train, curr_y_train)

    for x, y in curr_testing:
        y_hat = forest.predict(x)
        if y_hat == 0:
            if y == 0:
                tns[i] += 1
            else:
                fns[i] += 1
        else:
            if y == 0:
                fps[i] += 1
            else:
                tps[i] += 1

with open('results.csv', 'w') as fp:
    csvWriter = csv.writer(fp, delimiter=',')
    csvWriter.writerow(fps)
    csvWriter.writerow(fns)
    csvWriter.writerow(tps)
    csvWriter.writerow(tns)

accuracies = []
precisions = []
recalls = []
f_measures = []
for i in range(NUM_SLICES):
    accuracies.append((tps[i] + tns[i]) / float(tps[i] + tns[i] + fps[i] + fns[i]))
    precisions.append(tps[i] / float(tps[i] + fps[i]))
    recalls.append(tps[i] / float(tps[i] + fns[i]))
    f_measures.append((2 * tps[i]) / float(2 * tps[i] + fps[i] + fns[i]))

with open('measures.csv', 'w') as fp:
    csvWriter = csv.writer(fp, delimiter=',')
    csvWriter.writerow(accuracies)
    csvWriter.writerow(precisions)
    csvWriter.writerow(recalls)
    csvWriter.writerow(f_measures)

accuracy = sum(accuracies) / len(accuracies)
precision = sum(precisions) / len(precisions)
recall = sum(recalls) / len(recalls)
f_measure = sum(f_measures) / len(f_measures)

print "Accuracy: " + str(accuracy)
print "Precision: " + str(precision)
print "Recall: " + str(recall)
print "F-Measure: " + str(f_measure)
