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
This approach has two limitations:
- The problem of unidirectionality.
- The problem of not accounting for the scope of interests.

### About the project structure:
- `tg`: Short for Telegram.
- `classes dirs`: Mostly the same as models (should be renamed).
  
#### Folders:
- `ptb`: Short for Python Telegram Bot, a framework for Telegram.
- `tg/ptb/actions`: Common shared actions for multiple ptb handlers.
- `tg/ptb/views`: Modules responsible for sending responses from the bot to the user 
   (e.g., sending "Hello", updating message icons, etc. This is probably a poorly-designed feature.)
- `tg/ptb/views/cjm`: CJM stands for Customer Journey Map—a set of public/personal scenarios. 
   This is the key and final view with which the user will interact. 
   It reflects user behavior from top to bottom and utilizes various view modules like collections, posts, etc.
- `tg/ptb/handlers_definition`: The place where all handlers are defined.
- `services`: Classes to handle a group of models.
- `models/base`: Base for independent models (models that do not depend on other models).
- `mix`: A mix of small classes that aren't enough to fill a whole module.
- `collections`: Collections of posts.


### Locales:
Why are locale IDs similar to `var_name` rather than to a usual string?
- Because I was not aware that IDs could change their plurality form depending on the message. 
  Therefore, I used variable names (should be improved).

### Forms:
- Fields that the user must fill in to continue (similar to HTML forms).

### custom_ptb:
My attempts to improve a deprecated version of ptb; only the `ConversationHandler` is in use. 
- I use "prefallbacks" to catch the event before it continues to the handler itself.

### Channels:
Telegram implementation uses two channels:
- **Posts Channel**: A channel that delivers posts directly to users.
- **Posts Store Channel**: A temporary place to own user-created posts (this way, users cannot alter or forge post content).

### Inside the code:
**Mapper**: A quick but flawed way to substitute classes and outcome model types.
  Provides the necessary classes from the appropriate layer.
    Example: The Telegram layer has its own mapper, as does the ptb layer.
  **Better Approach:** 
     - Use composition.
     - Pass the required layer classes to the initializer.
     - Create classes through the factory pattern.
  **Note:** 
     - Quick overriding of the outcome model type is possible without redefining every model method.
     - However, this is bad design.

- `update.callback_query.answer()`  
  - Breaks down the "wait" indicator after a button click.

- `from __future__ import annotations`  
  - Required when used in combination with `typing.TYPE_CHECKING` to avoid a 'not defined' error.

### CMDS:
Create translations command:  
- `msgfmt -o messages.mo messages.po`

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
- TODO: Paste link here
