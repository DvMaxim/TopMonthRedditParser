#This API will store posts received from client in the result database.

##List of operations handled by the server.

###1) Receive all posts from the database source:

- Base URL: http://localhost:8087
- Resource: /posts
- Http method: GET

```bash
http://localhost:8087/posts
```
###2) Receive necessary post by unique post id

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: post_id
- Http method: GET

```bash
http://localhost:8087/posts?post_id=88881926744411ec8919dcf505e0cd11
```

###3) Add necessary post in the database.

- Base URL: http://localhost:8087
- Resource: /posts
- Http method: POST
- Sample body: {
"unique_id": "7595d82853df11eca36cdef505e0cd95", 
"post_link": "b'https://www.reddit.com/r/nextfuckinglevel/comments/qtpafl/i_spent_300_hours_making_this_monster_hunter/'", 
"username": "KamuiCosplay", 
"user_karma": "185,269", 
"user_cake_day": "November 28, 2011", 
"post_karma": "95,596", 
"comment_karma": "15,696", 
"post_date": "14 Nov 2021", 
"number_of_comments": "2.9k", 
"number_of_votes": "149k", 
"post_category": "nextfuckinglevel\n"
}
- Note: Body performed by JSON format.
- Sample response: {"7595d82853df11eca36cdef505e0cd95": 2}
```bash
http://localhost:8087/posts
```

###4) Delete post from the database.

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: post_id
- Http method: DELETE

```bash
http://localhost:8087/posts?post_id=88881926744411ec8919dcf505e0cd11
```

###5) Change post from the database on a necessary one.

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: post_id
- Http method: PUT
- Sample body: {
"post_link": "b'https://www.reddit.com/r/nextfuckinglevel/comments/qtpafl/i_spent_300_hours_making_this_monster_hunter/'", 
"username": "KamuiCosplay", 
"user_karma": "185,269", 
"user_cake_day": "November 28, 2011", 
"post_karma": "95,596", 
"comment_karma": "15,696", 
"post_date": "14 Nov 2021", 
"number_of_comments": "2.9k", 
"number_of_votes": "149k", 
"post_category": "nextfuckinglevel\n"
}
- Note: Body performed by JSON format.
- Note: Here you have no unique id value in the sample structure. The reason for this is that you 
        can't change the unique id of the post.

```bash
http://localhost:8087/posts?post_id=88881926744411ec8919dcf505e0cd11
```

