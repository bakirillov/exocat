# exocat
Personal exocortex manager

This is a prototype. Expect breaking changes.


## Manual

View help with `python exocat.py --help`.

### Card management
`new -t TITLE` - create a new card in the exocortex. CARD_ID is formed based on the current date and time;    
`edit -c CARD_ID` - edit a card with given ID;    
`view -c CARD_ID` - view a card with given ID;    
`random` - edit a random card;     
Encasing a [[word]] in square bracket would make the Exocat to create a new card with this word as a title

### Card queries
`query -r REGEX -s SECTION` - find a set of cards that match given regex in a given section.    
Section could be "title", "description", "contents", "questions", "answers". A "full" option performs a full-text search.   
An option `-v` lets view the latest card in a query result and an option `-o` opens the latest card in an editor.   

### Link management
`index -t TYPE` - construct an index over existing files. TYPE could be "all", "explicits" and "implicits".    
There could be two kinds of links:    
1. Explicit links - the links explicitly set by the user. Making the hashtag of a \#word would make the word a node in a graph of explicit links;   
2. Implicit links - the links implicitly formed by the language analysis. Shared non stop-word nouns and verbs form implicit links.   
`overview -r REGEX` - view the existing links in the index and filter them using a regex;    

### Study mode
`study` - runs the study mode: Leitner box spaced repetition;    
Option `--reindex` - go over the cards and get new question-answer pair;    
Option `--catch-up` - limits the number of cards in a study session to 25;    

### Idea mode
`idea` - manage a list of ideas;     
No options - print the list of ideas;      
Option `-n IDEA, --new IDEA` - add a new idea to the list;     
Option `-s IDEA_NUMBER, --solve IDEA_NUMBER` - remove the idea from the list;     

### Card merging
`include` - add a .md file as a card;         
Option `-f, --file` sets the file to add;        
Option `-m, --merge` - id of the card to merge our file with. If not set, `include` will copy everything from the file into a new card.      

### Miscellanea
`media -c CARD_ID` - view media files associated with the specified card;    
`unfinished -i CARD_ID -c COMMENT` - add a card into the unfinished list with a specified comment. The repeated application removes from the list.      
Run `unfinished` with no options to list all the unfinished cards.     

### Migration
If you have used exocat before the 0.5 version, run `python migrate.py --version 0.5 --path /path/to/your/exocortex` to convert the existing exocortex into 0.5 format.

## TODO:
1. Readme and tutorial    
2. pip package   
3. Neo4J support  
4. Web UI   

