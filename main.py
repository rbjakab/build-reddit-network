from credentials import reddit, db
from aux import getCurrentTime, getUserSubreddits, addElementToSetLimit, limitSetSize, getUserThreads
import settings


try:
    settings.loadSettings()
except Exception as Exception0:
    print("Load settings exception:", Exception0)

# get the popular subreddits in Reddit
sub_queue = set()
for subreddit in reddit.subreddits.popular():
    try:
        sub_queue.add(subreddit.display_name)
    except:
        continue

thread_queue = set()
user_queue = set()
visited_users = set()

# thread:    Submission
# comments:  CommentForest

while len(sub_queue) > 0:
    if len(thread_queue) == 0:
        sub = sub_queue.pop()

        # get the current subreddit's ~1000 hottest threads
        for thread in reddit.subreddit(sub).hot(limit=settings.data["api_limit"]):
            try:
                addElementToSetLimit(thread_queue, thread, set_size=settings.data["size_limit"]["thread"])
            except:
                continue

    while len(thread_queue) > 0:
        thread = thread_queue.pop()

        # try to add the thread's author to the user queue
        try:
            addElementToSetLimit(user_queue, thread.author.name, set_size=settings.data["size_limit"]["user"])
        except:
            pass

        print("Fetching https://reddit.com{}".format(thread.permalink))
        thread.comments.replace_more(limit=10)
        comments = thread.comments.list()

        # go through the thread's comments and adds the comments' authors to the user queue
        for comment in comments:
            try:
                addElementToSetLimit(user_queue, comment.author.name, set_size=settings.data["size_limit"]["user"])
            except:
                print("Problem with author of this comment:", comment)
                continue

        user_queue = user_queue - visited_users

        while len(user_queue) > 0:
            # load the settings
            try:
                settings.loadSettings()
            except Exception as Exception0:
                print("Load settings exception:", Exception0)

            try:
                user_name = user_queue.pop()
                user = reddit.redditor(user_name)

                # check if the user is visited in the last short time
                if user in visited_users:
                    print("{} user is already visited.".format(user))
                    continue

                # check if the user is visited in the last `settings.data["last_fetched_days"]` days
                doc_ref = db.collection("reddit").document("db").collection("users").document(user_name)
                doc = doc_ref.get()

                max_subreddits_length = 0

                if doc.exists:
                    lastFetched = doc.to_dict()["__lastFetched"]
                    max_subreddits_length = doc.to_dict()["__len"]

                    duration_in_s = (getCurrentTime() - lastFetched).total_seconds()
                    days = divmod(duration_in_s, 86400)[0]
                    if days < settings.data["last_fetched_days"]:
                        print(
                            "{} is already fetched less than {} days ago.".format(
                                user_name, settings.data["last_fetched_days"]
                            )
                        )
                        continue

                # remove those subreddits which have the same name as the meta informations
                user_subreddits = getUserSubreddits(user) - set(["__user", "__lastFetched", "__len"])
                user_threads = getUserThreads(user)

                print(
                    "\nsub_queue: {}, thread_queue: {}, user_queue: {}, visited_users: {}".format(
                        len(sub_queue), len(thread_queue), len(user_queue), len(visited_users)
                    ),
                )

                objectToWrite = {
                    "__user": user_name,
                    "__lastFetched": getCurrentTime(),
                    "__len": max(len(list(user_subreddits)), max_subreddits_length),
                }

                for sub in list(user_subreddits):
                    objectToWrite[sub] = True

                db.collection("reddit").document("db").collection("users").document(user_name).set(
                    objectToWrite, merge=True
                )

                print("user: {}, len: {}".format(user_name, len(list(user_subreddits))), "\n")

                sub_queue = sub_queue | user_subreddits
                thread_queue = thread_queue | user_threads

                thread_queue = limitSetSize(thread_queue, set_size=settings.data["size_limit"]["thread"])
                sub_queue = limitSetSize(sub_queue, set_size=settings.data["size_limit"]["sub"])
                addElementToSetLimit(visited_users, user, set_size=settings.data["size_limit"]["visited"])
            except Exception as Exception1:
                try:
                    print("-- FAILED -- {}, exception: {}".format(user_name, Exception1))
                except Exception as Exception2:
                    print("-- FAILED -- None, exception[1,2]: {}, {}".format(Exception1, Exception2))
                pass
