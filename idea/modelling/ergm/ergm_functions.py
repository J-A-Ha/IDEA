"""Functions for running Exponential Random Graph Model (ERGM) analysis on networks.

Code implementation utilises the RPy2 package to emulate R's ERGM library. 

Notes
-----
See documentation:
    * RPy2: https://rpy2.github.io/doc/latest/html/index.html
    * R ERGM: https://cran.r-project.org/web/packages/ergm/ergm.pdf 
"""


def casenet_fit_ergm(self, network = 'request_input', terms = 'edges'):
    
    """
    Fits Expontential Random Graph Model to network from CaseNetworkSet.
    
    Parameters
    ----------
    network : str, igraph.Graph, NetworkX, or CaseNetwork
        network object to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    
    Returns
    -------
    result : object
        fitted ERGM.
    """
    
    # Requesting network name from user input if none provided
    if network == 'request_input':
        network = input('Network name: ')
    
    # Retrieving network object
    network = self.get_network(network)
    
    # Fitting ERGM
    return network.fit_ergm(terms = terms)

def case_fit_ergm(self, network = 'request_input', terms = 'edges'):
    
    """
    Fits Expontential Random Graph Model to network from Case.
    
    
    Parameters
    ----------
    network : str, igraph.Graph, NetworkX, or CaseNetwork
        name of network object to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    
    Returns
    -------
    result : object
        fitted ERGM.
    """
    
    # Requesting network name from user input if none provided
    if network == 'request_input':
        network = input('Network name: ')
    
    # Retrieving network object and fitting ERGM
    return self.networks.fit_ergm(network = network, terms = terms)
    


def create_ergm(network, terms: list = ['edges']):
    
    """
    Initialises an Expontential Random Graph Model using selected terms as modelling parameters.
    
    Parameters
    ----------
    network : igraph.Graph, NetworkX, or CaseNetwork
        network object to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    
    Returns
    -------
    result : object
        fitted ERGM.
    """
    
    # Checking type of terms; if string, wrapping as a list
    if type(terms) is str:
        terms = [terms]
    
    # Checking type of network; if NetworkX, converting to igraph.Graph
    if (
            (type(network) == NetworkX_Undir)
            or (type(network) == NetworkX_Dir)
            or (type(network) == NetworkX_Multi)
        ):
             network = Graph.from_networkx(network)
    
    # Generating adjacency matrix
    adjMat = network.get_adjacency()
    adjMat = np.array(adjMat.data)
    
    # Creating R network object from adjacency matrix
    input_network = networkr.network(adjMat)
    
    # Creating formula string for R code
    formula_str = 'input_network ~'
    
    # Adding terms to formula
    count = 1
    for term in terms:
        if count > 1:
            term = '+ ' + term
        formula_str = formula_str + ' ' + term
        count += 1
    
    # Setting up R environment using formula string
    formula = Formula(formula_str)
    env = formula.environment
    env['input_network'] = input_network
    
    # Creating ERGM in R
    output = ergm.ergm(formula)
    
    return output



def fit_ergm(network, terms: list = ['edges'], print_results = True):
    
    """
    Fits an Expontential Random Graph Model using selected terms as modelling parameters.
    
    Parameters
    ----------
    network : str, igraph.Graph, NetworkX, or CaseNetwork
        network object to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    print_results : bool
        whether to print results to the console. Defaults to True.
    
    Returns
    -------
    result : dict
        dictionary of ERGM results.
    """
    
    # Creating ERGM
    output = create_ergm(network = network, terms = terms, from_case = from_case, case = case)
    
    # Getting summary data
    summary = base.summary(output)

    # Converting to dictionaries for parsing
    output_dict = dict(zip(output.names, output))
    summary_dict = dict(zip(summary.names, summary))
    
    # Parsing output and summary
    formula_used = str(output_dict['formula']).replace('\n', '')
    model_ref = str(output_dict['reference']).split('\n')[0].replace('~', '')
    ergm_version = text_splitter(
                                str(output_dict['ergm_version']), 
                                parse_by = ' ', 
                                replace = ["‘", "’", '[1]', '\n']
                                )[0]
    
    values = [
                'R ERGM Library', 
                ergm_version, 
                formula_used, 
                model_ref, 
                output_dict['estimate'][0], 
                output_dict['MCMCtheta'][0]
                ]
    
    # Creating dataframe for output data
    about_model = pd.DataFrame(
                                values, index = [
                                                'Package used', 
                                                'Version', 
                                                'Formula', 
                                                'Model Reference', 
                                                'Estimation Method', 
                                                'MCMC Theta'
                                                ], 
                                columns = ['']
                                )
    
    # Cleaning output data
    network_attr = text_splitter(str(output_dict['network']), parse_by = '\n')
    
    # Retrieving model network attributes and assigning to dictionary
    network_attr_dict = {}
    network_attr_dict[network_attr[0]] = network_attr[1:-3]
    network_attr_dict[network_attr[-3]] = network_attr[-2]
    network_attr_dict[network_attr[-1]] = None

    # Retrieving model covariance matrices
    cov_mats_list = [
                    summary_dict['asycov'][0][0], 
                    summary_dict['asyse'][0]
                    ]
    
    # Creating dataframe for model covariance matrices
    cov_mats = pd.DataFrame(
                            cov_mats_list, 
                            index = [
                                        'Asymptotic Covariance Matrix', 
                                        'Asymptotic Standard Error Matrix'
                                    ], 
                            columns = ['']
                            )
    
    # Creating dataframe for model coefficients
    coefs = pd.DataFrame(
                        summary_dict['coefficients'][0], 
                        index = [
                                'Estimate', 
                                'Std. Error', 
                                'MCMC %', 
                                'z value', 
                                'Pr (>|z|)'
                                ], 
                        columns = ['edges']
                        ).transpose()

    # Creating dataframe for model deviance
    deviance = pd.DataFrame(
                            summary_dict['devtable'], 
                            index = [
                                    'Null Deviance', 
                                    'Residual Deviance'
                                    ], 
                            columns = [
                                        'Value', 
                                        'Degrees of Freedom'
                                        ]
                            ).transpose()
    
    # Creating array for model likelihood ratios
    lr_array = [
                summary_dict['mle.lik'][0], 
                summary_dict['null.lik'][0]
                ]
    lrs = pd.DataFrame(lr_array, index = ['MLE', 'NULL'], columns = ['LE']).transpose()
    
    coefs_df = coefs['Estimate'].to_frame()

    coefs_df = coefs_df['Estimate'].apply(inv_logit)
    if isinstance(coefs_df, pd.DataFrame):
        coefs_df = coefs_df.rename(columns={"Estimate": "Probability"})
    
    # Bundling results into a dictionary
    results = {
                'about_model': about_model,
                'network_attributes': network_attr_dict,
                'covariance_matrices': cov_mats,
                'coefficients': coefs,
                'probabilities': coefs_df,
                'deviance': deviance,
                'likelihood_ratios': lrs
              }
    
    if print_results == True:
        
        # Printing results
        for key in results.keys():

            print('\n - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
            print('\n'+key+'\n')

            if key == 'network_attributes':
                for item in results[key]['Network attributes:']:
                    print(item)

            elif key == 'coefficients':
                print(results[key])
                print('\n Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1')

            else:
                print(results[key])

        print('\n - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
    
    return results

def edge_probabilities(self, terms = ['edges']):
    
    """
    Calculates edge probabilities for a fitted Expontential Random Graph Model using selected terms as modelling parameters.
    
    Parameters
    ----------
    terms : str or list
        name or list of name of terms for formula.
    """
    
    return ergm_edge_probabilities(network = self, terms = 'edges', from_case = False, case = None)

def casenet_edge_probabilities(self, network = 'request_input', terms = 'edges'):
    
    """
    Calculates edge probabilities for a fitted Expontential Random Graph Model using selected terms as modelling parameters.
    
    Parameters
    ----------
    network : str
        name of network object from Case to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    """
    
    # Requesting network name from user input if none provided
    if network == 'request_input':
        network = input('Network name: ')
    
    # Retrieving network object
    network = self.get_network(network)
    
    # calculating edge probabilities
    return network.edge_probabilities(terms = terms)

def case_edge_probabilities(self, network = 'request_input', terms = 'edges'):
    
    """
    Calculates edge probabilities for a fitted Expontential Random Graph Model using selected terms as modelling parameters.
    
    Parameters
    ----------
    network : str
        name of network object from Case to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    """
    
    return self.networks.edge_probabilities(network = network, terms = terms)

def ergm_edge_probabilities(network, terms = ['edges']):
    
    """
    Calculates edge probabilities for a fitted Expontential Random Graph Model using selected terms as modelling parameters.
    
    Parameters
    ----------
    network : igraph.Graph, NetworkX, or CaseNetwork
        network object to fit ERGM to.
    terms : str or list
        name or list of name of terms for formula.
    
    Returns
    -------
    result : pandas.DataFrame
        dataframe of edge probabilities.
    """
    
    # Checking type of terms; if string, wrapping as a list
    if type(terms) is str:
        terms = [terms]
    
    # Checking type of network; if NetworkX, converting to igraph.Graph
    if (
            (type(network) == NetworkX_Undir)
            or (type(network) == NetworkX_Dir)
            or (type(network) == NetworkX_Multi)
        ):
             network = Graph.from_networkx(network)

    # Generating adjacency matrix
    adjMat = network.get_adjacency()
    adjMat = np.array(adjMat.data)
    
    # Creating R network object from adjacency matrix
    input_network = networkr.network(adjMat)

    # Creating formula string to input into R
    formula_str = 'input_network ~'
    
    # Adding terms to formula
    count = 1
    for term in terms:
        if count > 1:
            term = '+ ' + term
        formula_str = formula_str + ' ' + term
        count += 1
    
    # Setting up R environment using formula string
    formula = Formula(formula_str)
    env = formula.environment
    env['input_network'] = input_network
    
    # Fitting ERGM
    output = ergm.ergm(formula)
    
    # Retrieving results
    output_dict = dict(zip(output.names, output))
    
    # Retrieving edge probabilities values
    theta_val = output_dict['MCMCtheta'][0]
    probs = ergm.predict_formula(formula, theta = theta_val)
    
    # Converting to dataframe
    with (robjects.default_converter + pandas2ri.converter).context():
        df = robjects.conversion.get_conversion().rpy2py(probs)
    
    # Formatting dataframe
    df['tail'] = df['tail'].astype(int)
    df['head'] = df['head'].astype(int)
    df = df.rename(columns={"p": "P(edge)"})

    return df