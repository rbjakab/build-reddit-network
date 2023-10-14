from credentials import db


def saveData(data):
    db.collection('users').document(data['user']).set({
        'user': data['user'],
        'lastFetched': data['lastFetched'],
        'subreddits': data['subreddits']
    }, merge=True)
