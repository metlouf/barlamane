#!/usr/bin/env python3
import datetime
import json
import pydgraph
from enum import Enum, auto

from check_data import extract_commissions_from_deputies, extract_commissions_from_laws, extract_ministry_from_questions, process_commission


class DgraphConnection:
    """Manages the connection to Dgraph database."""
    def __init__(self, host='localhost', port='9080'):
        """
        Initialize Dgraph client connection.
        
        :param host: Dgraph server host
        :param port: Dgraph server port
        """
        self.client_stub = pydgraph.DgraphClientStub(f'{host}:{port}')
        self.client = pydgraph.DgraphClient(self.client_stub)

    def drop_all(self):
        """Drop all data in the database."""
        return self.client.alter(pydgraph.Operation(drop_all=True))

    def set_schema(self):
        """Define schema for Political System."""
        schema = """
        name: string @index(exact) .
        title: string @index(exact) .
        type: string @index(exact) .
        state: string @index(exact) .
        party: string @index(exact) .
        link: string .
        created_at: datetime .

        # Add this line to define the minister predicate for Ministry
        minister: uid .

        deputy: [uid] .
        law: [uid] .
        question: [uid] .
        commission: [uid] .
        ministry: uid .
        work_at: uid .
        developed_by : uid .

        type Deputy {
            name
            party
            work_at
            ask
        }

        type Minister {
            name
            party
            work_at
        }

        type Commission {
            name
        }

        type Ministry {
            name
        }

        type Law {
            title
            type
            link
            created_at
            developed_by
        }
        """
        return self.client.alter(pydgraph.Operation(schema=schema))
    def close(self):
        """Close the client stub connection."""
        self.client_stub.close()


class Law:
    """Represents a law in the legislative system."""
    def __init__(self, title, law_type, link=None):
        """
        Initialize a Law.
        
        :param title: Title of the law
        :param law_type: Type of the law
        :param link: Optional link to the law document
        :param state: Current state of the law
        """
        self.uid = None
        self.title = title
        self.law_type = law_type
        self.link = link
        self.created_at = datetime.datetime.now()
        self.commission = None

    def update_state(self, new_state):
        """
        Update the state of the law.
        
        :param new_state: New state for the law
        """
        self.state = new_state

    def to_dict(self):
        """
        Convert Law object to a dictionary for Dgraph mutation.
        
        :return: Dictionary representation of the Law
        """
        law_dict = {
            'dgraph.type': 'Law',
            'title': self.title,
            'type': self.law_type,
            'link': self.link,
            'created_at': self.created_at.isoformat()
        }
        
        if self.commission:
            print(self.commission.to_dict())
            law_dict['developed_by'] = self.commission.to_dict()
        
        if self.uid:
            law_dict['uid'] = self.uid
        
        return law_dict


class Commission:
    """Represents a legislative commission."""
    def __init__(self, name):
        """
        Initialize a Commission.
        
        :param name: Name of the commission
        """
        self.uid = None
        self.name = name

    def create_law(self, title, law_type, link=None):
        """
        Create a new law within this commission.
        
        :param title: Title of the law
        :param law_type: Type of the law
        :param link: Optional link to the law document
        :return: Created Law object
        """
        law = Law(title, law_type, link)
        law.commission = self
        return law

    def to_dict(self):
        """
        Convert Commission object to a dictionary for Dgraph mutation.
        
        :return: Dictionary representation of the Commission
        """
        commission_dict = {
            'dgraph.type': 'Commission',
            'name': self.name
        }
        
        if self.uid:
            commission_dict['uid'] = self.uid
        
        return commission_dict


class PoliticalRepresentative:
    """Base class for political representatives."""
    def __init__(self, name, party):
        """
        Initialize a political representative.
        
        :param name: Representative's name
        :param party: Political party
        """
        self.uid = None
        self.name = name
        self.party = party


class Deputy(PoliticalRepresentative):
    """Represents a Deputy in the political system."""
    def __init__(self, name, party):
        """
        Initialize a Deputy.
        
        :param name: Deputy's name
        :param party: Political party
        """
        super().__init__(name, party)
        self.commissions = []

    def add_commission(self, commission):
        """
        Add a commission to the deputy.
        
        :param commission: Commission to add
        """
        self.commissions.append(commission)

    def to_dict(self):
        """
        Convert Deputy object to a dictionary for Dgraph mutation.
        
        :return: Dictionary representation of the Deputy
        """
        deputy_dict = {
            'dgraph.type': 'Deputy',
            'name': self.name,
            'party': self.party,
            'work_at': [commission.to_dict() for commission in self.commissions]
        }
        
        if self.uid:
            deputy_dict['uid'] = self.uid
        
        return deputy_dict


class Ministry:
    """Represents a ministry in the political system."""
    def __init__(self, name):
        """
        Initialize a Ministry.
        
        :param name: Name of the ministry
        """
        self.uid = None
        self.name = name

    def to_dict(self):
        """
        Convert Ministry object to a dictionary for Dgraph mutation.
        
        :return: Dictionary representation of the Ministry
        """
        ministry_dict = {
            'dgraph.type': 'Ministry',
            'name': self.name
        }
        
        
        if self.uid:
            ministry_dict['uid'] = self.uid
        
        return ministry_dict


class Minister(PoliticalRepresentative):
    """Represents a Minister in the political system."""
    def __init__(self, name, party, ministry):
        """
        Initialize a Minister.
        
        :param name: Minister's name
        :param party: Political party
        :param ministry: Ministry they lead
        """
        super().__init__(name, party)
        self.ministry = ministry
        ministry.minister = self

    def to_dict(self):
        """
        Convert Minister object to a dictionary for Dgraph mutation.
        
        :return: Dictionary representation of the Minister
        """
        minister_dict = {
            'dgraph.type': 'Minister',
            'name': self.name,
            'party': self.party,
            'work_at':  self.ministry.to_dict()
        }
        
        if self.uid:
            minister_dict['uid'] = self.uid
        
        return minister_dict


class DgraphPoliticalSystemManager:
    """Manages Political System operations in Dgraph."""
    def __init__(self, connection):
        """
        Initialize PoliticalSystemManager with a Dgraph connection.
        
        :param connection: DgraphConnection instance
        """
        self.connection = connection

    def create_representative(self, representative):
        """
        Create a representative in the database.
        
        :param representative: Deputy or Minister object to create
        :return: UID of the created representative
        """
        txn = self.connection.client.txn()
        try:
            # Mutation to create representative and associated entities
            if isinstance(representative, Deputy):
                # Create commissions first
                for commission in representative.commissions:
                    if commission.uid == None :
                        commission_response = txn.mutate(set_obj=commission.to_dict())
                        commission.uid = list(dict(commission_response.uids).values())[0]
            
            elif isinstance(representative, Minister):
                # Create ministry
                if representative.ministry.uid == None :
                    ministry_response = txn.mutate(set_obj=representative.ministry.to_dict())
                    representative.ministry.uid = list(dict(ministry_response.uids).values())[0]

            # Create the representative
            response = txn.mutate(set_obj=representative.to_dict())
            txn.commit()
            
            # Update representative's UID
            representative.uid = list(dict(response.uids).values())[0]
            
            return representative.uid

        except Exception as e:
            print(f"Error creating representative: {e}")
            txn.discard()
            raise
        finally:
            txn.discard()

    def query_representative(self, name, rep_type=None):
        """
        Query a representative by name and optionally by type.
        
        :param name: Name of the representative to query
        :param rep_type: Type of representative (Deputy or Minister)
        :return: List of matching representatives
        """
        # Base query for all representatives
        query = """query all($a: string, $type: string) {
            all(func: eq(name, $a)) @filter(type($type)) {
                uid
                name
                party
                type
                commission{
                    uid
                    name
                }
            }
        }"""

        # Prepare variables
        variables = {'$a': name}
        if rep_type:
            variables['$type'] = rep_type
        else:
            # If no type specified, use a default that matches no type
            query = query.replace('@filter(type($type))', '')

        # Execute query
        res = self.connection.client.txn(read_only=True).query(query, variables=variables)
        return json.loads(res.json)['all']

    def create_law_in_commission(self, commission, title, law_type, link=None):
        """
        Create a law in a specific commission.
        
        :param commission: Commission to add the law to
        :param title: Title of the law
        :param law_type: Type of the law
        :param link: Optional link to the law document
        :return: Created Law object
        """
        law = commission.create_law(title, law_type, link)
        
        # Update the commission in the database
        txn = self.connection.client.txn()
        try:
            
            response = txn.mutate(set_obj=law.to_dict())
            txn.commit()
            
            # Update law's UID
            law.uid = list(dict(response.uids).values())[0]
            return law
        except Exception as e:
            print(f"Error creating law in commission: {e}")
            txn.discard()
        finally:
            txn.discard()


def old_main():
    # Create Dgraph connection
    connection = DgraphConnection()
    
    # Drop all existing data and set schema
    connection.drop_all()
    connection.set_schema()
    
    # Create political system manager
    pol_manager = DgraphPoliticalSystemManager(connection)
    
    # Create a commissions
    budget_commission = Commission('Budget and Finance Commission')

    # Create Ministries
    education_ministry = Ministry('Ministry of Education')
    
    ## Create Deputies
    deputy1 = Deputy('John Smith', 'Progressive Party')
    deputy2 = Deputy('Emily Johnson', 'Liberal Party')
    #
    
    ## Add deputies to commission
    deputy1.add_commission(budget_commission)
    deputy2.add_commission(budget_commission)
    ##
    ### Create laws in the commission
    ##
    ### Create a Ministry
    
    
    ## Create a Minister
    minister1 = Minister('Sarah Williams', 'Conservative Party', education_ministry)
    
    ## Create representatives in database
    pol_manager.create_representative(deputy1)
    pol_manager.create_representative(deputy2)
    
    ## Create laws
    education_funding_law = pol_manager.create_law_in_commission(
        budget_commission,
        title='Education Funding Act',
        law_type='Fiscal Policy',
        link='https://example.com/education-funding-law'
    )

    ## Create questions
    


    ## Query representatives
    deputy_results = pol_manager.query_representative('John Smith', 'Deputy')
    minister_results = pol_manager.query_representative('Sarah Williams', 'Minister')


    #
    print('Deputies:', json.dumps(deputy_results, indent=2))
    print('Ministers:', json.dumps(minister_results, indent=2))
    #
    ## Close connection
    connection.close()

def main():
    # Create Dgraph connection
    connection = DgraphConnection()
    
    # Drop all existing data and set schema
    connection.drop_all()
    connection.set_schema()
    
    # Create political system manager
    pol_manager = DgraphPoliticalSystemManager(connection)
    
    # Create a commissions
    commissions = set.union(extract_commissions_from_deputies(),extract_commissions_from_laws())

    dict_commissions = {}

    for c in commissions : 
        dict_commissions[c] = Commission(c)

    # Create Ministries

    ministries = extract_ministry_from_questions()
    dict_ministry = {}
    for c in ministries : 
        dict_ministry[c] = Ministry(c)

    ## Create Deputies
    
    with open('data/parliamentarians_arabic_2016_2021.json', 'r') as file:
        data = json.load(file)

    for deputy in data:
        deputy_g = Deputy(deputy['name'], deputy['party'])
        if 'function' in deputy:
            if "فريق" in deputy['function'] :
                pass
            else :
                commission_obj = dict_commissions[process_commission(deputy['function'])]
                deputy_g.add_commission(commission_obj)
        pol_manager.create_representative(deputy_g)
    
    ## Add deputies to commission

    ##
    ### Create laws in the commission
    with open('data/laws_arabic_version.json', 'r') as file:
        data = json.load(file)
    
    for project in data['projets_de_loi']:
        commission_obj = dict_commissions[process_commission(project['readings'][0]['commission'])]
        pol_manager.create_law_in_commission(
            commission_obj,
            title=project['title'],
            law_type='projets_de_loi',
            link=project['url']
        )
    
    
    for project in data['propositions_de_loi']:
        if len(project['readings'])>0 : 
            if 'commission' in project['readings'][0]:          
                commission_obj = dict_commissions[process_commission(project['readings'][0]['commission'])]
                pol_manager.create_law_in_commission(
                    commission_obj,
                    title=project['title'],
                    law_type='propositions_de_loi',
                    link=project['url']
                )
    
    for project in data['textes_de_loi']:
        commission_obj = dict_commissions[process_commission(project['commission'])]
        pol_manager.create_law_in_commission(
            commission_obj,
            title=project['title'],
            law_type='textes_de_loi',
            link=project['url']
        )


    ## Create questions
    


    ## Query representatives


    #

    #
    ## Close connection
    connection.close()


if __name__ == '__main__':
    try:
        main()
        print('DONE!')
    except Exception as e:
        print('Error: {}'.format(e))