## This file is meant to serve as documentation for the data_processor file

#### Function breakdown 
###### init:
The class is meant to take a csv path and generate a Dataframe; an analysis is then performed on the Dataframe and the Analysis is then written on a text file.
###### load_data:
SUMMARY: Load the file into a dataframe and take all the column names and pass them into the LLM to standardize the column names into [Driver,custumer name, price] etc. We then replace the existing column names with the LLM returned standardized versions.

We first check if the file path exists with a try and except block.
We load the csv into the dataframe and begin an Instance of the Hybridchatbot class - this will be used to standardize our column names
We write our prompt and pass current column names into the prompt
We then parse the LLM's generateed response with the parse function

###### parse_llm_response:
We strip the response string of any trailing and leading whitespaces and then we split the string by whitespaces and join them together
We then check to see if the reponse starts with `[` and ends with  `]`
We then remove the first and last letter of this string.
Then we split the string by the comma string and join them actual commas. 

###### generate_basic_stats:
We check for if the Dataframe exists.
We then use .describe() to write basic statistics.
price_stats is a dictionary.



#### Future updates
- add all ride info for minimal and maximum earned rides for each chauffeur
- Make dictionary for column synonyms and only use LLM for special cases.
- Account for other CSV's that are not Transportation related; Perform error handling.
