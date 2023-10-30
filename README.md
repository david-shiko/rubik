### About the project:
A dating app based on shared likes.

### How it works:
1. The admin publishes a post that is delivered to every bot user. Users can either like or dislike it.
2. Users can search for matches. To perform a search, a user should have liked at least a few posts.
3. To receive posts, users must be subscribed to the channel that publishes the posts.
4. The app searches the database for users who have liked the same posts as the searcher, based on the Jaccard Index.
5. Success! The user receives matches in descending order.

#### For example:
- UserA has liked 10 posts, UserB has liked 8 posts, and UserC has liked 6 posts.
- UserA searches and gets an 80% (8/10) match with UserB and a 60% (6/10) match with UserC.
- UserB searches and gets a 100% (8/8) match with UserA and a 75% (6/8) match with UserC.
- UserC searches and gets a 100% (6/6) match with both UserA and UserB.

#### Note:
This approach has two notable limitations:
- **The problem of asymmetry**:   
  With the Jaccard Index, User1 might find User2 as an ideal match, but User2 could consider User3 their ideal match.  
  This asymmetry may not reflect mutual compatibility.
- **Lack of weighted interests**:  
  The Jaccard Index doesn't consider the varying degrees of interest towards different posts.  
  All 'likes' are equal, providing no way to express varying levels of interest.

Despite these limitations, the Jaccard Index was selected for initial implementations for its simplicity.  
Cosine similarity solves these issues but is less intuitive and slightly more complex to implement.  
The primary focus is on the innovation of algorithmic pairing, making the specific choice of algorithm secondary.

### Channels:
Telegram implementation uses two channels:
- **Posts Channel**: A channel that delivers posts directly to users.
- **Posts Store Channel**: A temporary place to own user-created posts (this way, users cannot alter or forge post content).

### Deployment:
- Fill the `.env` file just as in `.env_sample`.
- Install dependencies with `pip install -r requirements.txt`.
- Run the tests (preferable): `pytest tests`.
- Run the app from the root folder: `python -m app`

### Why the project has some bad code in places:
I started this project when I still didn't know how to work with databases; I had to learn as I went along.  
Not every issue is worth fixing. The majority of questionable parts fall into the following categories:
- It was an interesting experiment.
- More data is needed to decide the direction for improvement.
- It's not key functionality.

### Demo:
#### Screenshots (need to make more):
![TG app screenshot](https://gcdnb.pbrd.co/images/lHAy1cuEY7dP.jpg?o=1)

#### Donations
While this donation most likely won't lead to any major changes, it will fill me with a warm sense of accomplishment.  
_"Wow, someone found this service useful enough to donate. Amazing! I've never received donations before."_

#### How to contribute:
I'm not experienced in managing large open-source projects on GitHub.  
Previously, I've only contributed to such projects rather than owning them.  
Your contributions are welcome.

[Buy Me A Coffee](https://www.buymeacoffee.com/davidshiko)

### Author: @david_shiko
- LI: https://www.linkedin.com/in/david-shiko/
- TG: https://t.me/david_shiko
- WA: https://wa.me/+972533999982
- @Email: [dsb321mp@gmail.com ](mailto:dsb321mp@gmail.com )
