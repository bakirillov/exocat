# exocat
Personal exocortex manager

 _._     _,-'""`-._     
(,-.`._,'(       |\`-/|     
____`-.-' \ )-`( , o o)     
__________`-    \`_`"'-     

## Manual

View help with `python exocat.py --help`.

### Card management
`new -t TITLE` - create a new card in the exocortex. CARD_ID is formed based on the current date and time;    
`edit -c CARD_ID` - edit a card with given ID;    
`view -c CARD_ID` - view a card with given ID;    
`random` - edit a random card;     

### Card queries
`query -r REGEX -s SECTION` - find a set of cards that match given regex in a given section.    
Section could be "title", "description", "contents", "questions", "answers". A "full" option performs a full-text search.   
An option `-v` lets view the latest card in a query result and an option `-o` opens the latest card in an editor.   

### Link management
`index -t TYPE` - construct an index over existing files. TYPE could be "all", "explicits" and "implicits".    
There could be two kinds of links:    
1. Explicit links - the links explicitly set by the user. Encasing a [[word]] in double square brackets make the word a node in a graph of explicit links;   
2. Implicit links - the links implicitly formed by the language analysis. Shared non stop-word nouns and verbs form implicit links.   
`overview -r REGEX` - view the existing links in the index and filter them using a regex;    
`links -c CARD_ID -t TYPE -r REGEX` - view the existing links of a particular card that belong to a type and match a regex;    

### Study mode
`study` - runs the study mode: Leitner box spaced repetition;    
Option `--reindex` - go over the cards and get new question-answer pair;    
Option `--catch-up` - limits the number of cards in a study session to 25;    

### Miscellanea
`media -c CARD_ID` - view media files associated with the specified card;    
`unfinished -i CARD_ID -c COMMENT` - add a card into the unfinished list with a specified comment. The repeated application removes from the list.      
Run `unfinished` with no options to list all the unfinished cards.     

## TODO:
1. Readme and tutorial    
2. pip package   
3. Neo4J support  
4. Web UI   
