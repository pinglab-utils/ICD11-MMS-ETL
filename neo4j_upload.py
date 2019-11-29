from neo4j import GraphDatabase
from time import sleep

#create driver fro neo4j so we can execute commands
driver= GraphDatabase.driver(uri = "bolt://localhost:7687", auth = ("neo4j","icd11"))

print('Starting upload script')
#get user input
clear_database = input('Would you like to clear the existing ICD11 codes?[y/n]: ').strip()
#if the input is not y or n ask for y or n
while(clear_database != 'y' and clear_database != 'n'):
    clear_database = input('Please use either y or n to indicate yes or no respectively').strip()
if(clear_database == 'y'):
    with driver.session() as sesh:
        print('\t Clearing database of ICD11 codes')
        sesh.run('MATCH (n:icd11_code) DETACH DELETE n')
        print('\t Cleared database of ICD11 codes')

import_nodes = input('Would you like to import the existing ICD11 codes?[y/n]: ').strip()
#if the input is not y or n ask for y or n
while(import_nodes != 'y' and import_nodes != 'n'):
    import_nodes = input('Please use either y or n to indicate yes or no respectively').strip()
if import_nodes == 'y':
    with driver.session() as sesh:
        #upload all nodes
        print('\t Starting node upload')
        sesh.run("""call apoc.load.json('file:///clean_mms_graph_data.json')
                yield value create (node:icd11_code) set node = value.props;""")
        print('\t Finished node upload')

        #create an index on the id of each node otherwise the following command
        #will take a while to run
        print('\t Creating index on id field''')
        sesh.run('''create index on :icd11_code(id)''')
        print('\t Index created, waiting 10 seconds before edge upload')

        ###create all the relevant relationships
        print('\t Starting edge upload')
        sesh.run("""match (n:icd11_code) with n , n.child_nodes as child_nodes
        match (m:icd11_code) where m.id in child_nodes  with n, m
        create (n)<-[:child_of]-(m)""")
        print('\t Finished edge upload')
print('Script has finished running')
