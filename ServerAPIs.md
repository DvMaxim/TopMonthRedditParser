#This API will store posts received from client in the result file.

##List of operations handled by the server.

###1) Receive all posts from the file source:

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: file_name
- Http method: GET
- Note: if file_name parameter misses server will use last proceeded file source.

```bash
http://localhost:8087/posts

http://localhost:8087/posts?file_name=<FILE_NAME>
```
###2) Receive necessary post by unique post id

- Base URL: http://localhost:8087
- Resource: /posts/<UNIQUE_ID>
- Query parameters: file_name
- Http method: GET
- Note: if file_name parameter misses server will use last proceeded file source.

```bash
http://localhost:8087/posts/<UNIQUE_ID>

http://localhost:8087/posts/<UNIQUE_ID>?file_name=reddit-202112031146.txt
```

###3) Add necessary post in the file source.

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: file_name
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
- Note: if file_name parameter misses server will use last proceeded file source.
- Note: Body performed by JSON format.
- Sample response: {"7595d82853df11eca36cdef505e0cd95": 2}
```bash
http://localhost:8087/posts

http://localhost:8087/posts?file_name=reddit-202112031436.txt
```

###4) Create file source with necessary name.

- Base URL: http://localhost:8087
- Resource: /filename
- Query parameters: file_name
- Http method: POST
- Sample body: {'file_name': file_name }
- Note: Body performed by JSON format.

```bash
http://localhost:8087/filename
```

###5) Delete post from the file source.

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: file_name
- Http method: DELETE
- Note: if file_name parameter misses server will use last proceeded file source.

```bash
http://localhost:8087/posts/<UNIQUE_ID>

http://localhost:8087/posts/<UNIQUE_ID>?file_name=<FILE_NAME>
```

###6) Change post from the file source on a necessary one.

- Base URL: http://localhost:8087
- Resource: /posts
- Query parameters: file_name
- Http method: PUT
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
- Note: if file_name parameter misses server will use last proceeded file source.
- Note: Body performed by JSON format.

```bash
http://localhost:8087/posts/<UNIQUE_ID>

http://localhost:8087/posts/<UNIQUE_ID>?file_name=<FILE_NAME>
```

