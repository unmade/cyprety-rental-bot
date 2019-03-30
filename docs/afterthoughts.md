## Afterthoughts

> tl;dr TCR is cool, but have some downsides. `mypy` is just cool_

_this is relevant for [this](https://github.com/unmade/cyprety-rental-bot/releases/tag/1.0.0) revision_

This bot is something I made just for fun to try out some ideas from clean architecture
and new [test && commit || revert (TCR)]((https://medium.com/@kentbeck_7670/test-commit-revert-870bbd756864))
workflow purposed by Kent Beck. I didn't want to try these things on small examples like fibonacci
and Telegram bot looked like a perfect candidate.

### test && commit || revert

As ridiculous as the whole approach sounds I decided to give it a try.

The whole project was written from scratch using TCR approach. 
Well, very few first commits I made using only first part (test && commit), hence I was 
scared of reverting my changes. After I got used to the flow I switch to fully TCR mode.

I use PyCharm for development and it was kind of tricky to set up it like Kent Beck do (run tcr on saved files)
cause autosave in PyCharm rules and manual one sucks :). Instead of this I use `Ctrl+R` shortcut to run TCR script.
You can find it in the [Makefile](Makefile) of this repo.

To summarize my experience with TCR - I liked it, maybe even more than TDD. 
I like how this approach makes you think different during development. 
It reminds drawing process - when you start with really primitive shapes and 
than start adding little by little more and more details.
I was especially interested in how it works on codebase larger than fibonacci example. Turns out not so bad.
All you have to do is think how to make your change in small steps and set right priorities.

What I don't like about TCR is really messed up git history. Say farewell to `git blame`, `git log` and 
verbose commit messages. I hope there will be a solution in the near future. 
By the way, `git squash` cannot be considered a solution due to how Kent Beck offers to use TCR.

I prepare some stats with [this script](https://gist.github.com/unmade/ba9a9ce9d62ec3f957dcc9a87fe620b5):

| Total number of commits        | 450  |
|--------------------------------|------|
| Median number of insertions    | 7.0  |
| Median number of deletions     | 3.0  |
| Median numbes of file changed  | 2.0  |

Table shows number of insertions and deletions per commit. 
I used median to exclude commits where I added a lot of lines 
(for example I added html file for test purposes that contains 7k lines!).
Original history preserved in [develop](https://github.com/unmade/cyprety-rental-bot/tree/develop) branch

### Clean architecture

Long time I believed clean architecture was not for python world,
but when type annotations and mypy came to the game things began to turn.

To my taste, resulting code looks more like java than python, but I like it anyway.
It looks clean, does what you expected it to do, shows your intention and it was easy to unit test.
It can be hard to understand for the first time, because of too much files, but after you got it its ok. 

I'm also concerned about too many lines of code. First version of this bot I wrote about year ago
consist of ~100 lines in total (though it wasn't async and not extensible and used shelve! as storage).
I also don't like [repositories](app/repositories.py), cause most of the methods just proxies to adapters.

This version has a lot of lines of code, but it's very easy to add another parser for site, or changed storage.

Also before start to actually write code I have idea about structure of the application which resulted in
this [gist](https://gist.github.com/unmade/f7f3d2e57e14a2919c5522ecc8df1d63). 
It was very cool to have that as starting point and it itself very convenient way to explain idea other person

First version of this bot I wrote in with about an hour, this project took much more time, but it was more fun :)
