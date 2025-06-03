// Initialize N3 store and SPARQL.js support
let store;
let loadedData = null;
let sparqlParser;
let sparqlGenerator;
let prefixes = {
    rdf: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    rdfs: 'http://www.w3.org/2000/01/rdf-schema#',
    xsd: 'http://www.w3.org/2001/XMLSchema#',
    myco: 'http://mycomind.org/kg/ontology/',
    entity: 'http://mycomind.org/kg/entity/'
};

// Initialize the store and SPARQL.js
async function initStore() {
    try {
        console.log('Initializing N3 store and SPARQL.js...');
        
        // Check if N3 is available
        if (typeof N3 === 'undefined') {
            throw new Error('N3 library not loaded');
        }
        
        // Check if SPARQL.js is available
        if (typeof sparqljs === 'undefined') {
            throw new Error('SPARQL.js library not loaded');
        }
        
        console.log('N3 available:', Object.keys(N3));
        console.log('SPARQL.js available');
        
        // Initialize N3 store
        store = new N3.Store();
        
        // Initialize SPARQL.js parser and generator with prefixes
        sparqlParser = new sparqljs.Parser({ prefixes: prefixes });
        sparqlGenerator = new sparqlGenerator({ prefixes: prefixes });
        
        console.log('N3 store and SPARQL.js initialized successfully');
        showStatus('info', 'RDF store ready. Loading knowledge graph...');
    } catch (error) {
        console.error('Failed to initialize:', error);
        showStatus('error', 'Failed to initialize: ' + error.message);
    }
}

// Load the knowledge graph data
async function loadLocalKnowledgeGraph() {
    try {
        showStatus('loading', 'Loading knowledge graph data...');
        
        try {
            // Try to load the JSON-LD file using fetch
            const response = await fetch('mycomind_knowledge_graph.jsonld');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const jsonldData = await response.json();
            console.log("Loaded JSON-LD data:", jsonldData);
            
            // Store the data for reference
            loadedData = jsonldData;
            
            // Process the JSON-LD data
            await processJSONLDToStore(jsonldData);
            
            // Count statements in the store
            const statementCount = store.size;
            console.log(`Loaded ${statementCount} statements into N3 store`);
            
            showStatus('success', `Loaded knowledge graph with ${statementCount} statements`);
            return true;
        } catch (fetchError) {
            console.error('Error fetching JSON-LD file:', fetchError);
            console.log('Loading sample data instead...');
            
            // Create sample data directly in the store
            createSampleData();
            
            // Count statements in the store
            const statementCount = store.size;
            console.log(`Created ${statementCount} statements from sample data in N3 store`);
            
            showStatus('success', `Loaded sample knowledge graph with ${statementCount} statements`);
            return true;
        }
    } catch (error) {
        console.error('Error loading knowledge graph:', error);
        showStatus('error', 'Error loading knowledge graph: ' + error.message);
        return false;
    }
}

// Create sample data directly in the N3 store
function createSampleData() {
    console.log("Creating sample data directly in the N3 store...");
    
    const { namedNode, literal } = N3.DataFactory;
    
    // Define common URIs
    const RDF_TYPE = namedNode('http://www.w3.org/1999/02/22-rdf-syntax-ns#type');
    const MYCO_NS = 'http://mycomind.org/kg/ontology/';
    const ENTITY_NS = 'http://mycomind.org/kg/entity/';
    
    // Define entity types
    const PERSON_TYPE = namedNode(MYCO_NS + 'RegenerativePerson');
    const PROJECT_TYPE = namedNode(MYCO_NS + 'Project');
    const HYPHALTIP_TYPE = namedNode(MYCO_NS + 'HyphalTip');
    
    // Define predicates
    const NAME_PRED = namedNode(MYCO_NS + 'name');
    const LOCATION_PRED = namedNode(MYCO_NS + 'location');
    const ROLE_PRED = namedNode(MYCO_NS + 'currentRole');
    const STATUS_PRED = namedNode(MYCO_NS + 'status');
    const ACTIVITY_STATUS_PRED = namedNode(MYCO_NS + 'activityStatus');
    const COLLABORATOR_PRED = namedNode(MYCO_NS + 'collaborator');
    
    // Create person: John
    const john = namedNode(ENTITY_NS + 'person/john');
    store.addQuad(john, RDF_TYPE, PERSON_TYPE);
    store.addQuad(john, NAME_PRED, literal('John Smith'));
    store.addQuad(john, LOCATION_PRED, literal('Portland, OR'));
    store.addQuad(john, ROLE_PRED, literal('Mycologist'));
    
    // Create person: Jane
    const jane = namedNode(ENTITY_NS + 'person/jane');
    store.addQuad(jane, RDF_TYPE, PERSON_TYPE);
    store.addQuad(jane, NAME_PRED, literal('Jane Doe'));
    store.addQuad(jane, LOCATION_PRED, literal('Seattle, WA'));
    store.addQuad(jane, ROLE_PRED, literal('Researcher'));
    
    // Create project: MycoMind
    const mycomind = namedNode(ENTITY_NS + 'project/mycomind');
    store.addQuad(mycomind, RDF_TYPE, PROJECT_TYPE);
    store.addQuad(mycomind, NAME_PRED, literal('MycoMind Project'));
    store.addQuad(mycomind, STATUS_PRED, literal('Active'));
    store.addQuad(mycomind, COLLABORATOR_PRED, john);
    
    // Create hyphal tip: Knowledge Graph
    const kg = namedNode(ENTITY_NS + 'hyphaltip/knowledge_graph');
    store.addQuad(kg, RDF_TYPE, HYPHALTIP_TYPE);
    store.addQuad(kg, NAME_PRED, literal('Knowledge Graph Implementation'));
    store.addQuad(kg, ACTIVITY_STATUS_PRED, literal('In Progress'));
    store.addQuad(kg, COLLABORATOR_PRED, jane);
    
    console.log("Sample data created successfully");
}

// Convert JSON-LD to RDF quads and add to N3 store
async function processJSONLDToStore(jsonldData) {
    try {
        console.log("Converting JSON-LD to N3 store...");
        
        // Process each entity in the @graph
        if (jsonldData["@graph"]) {
            jsonldData["@graph"].forEach(entity => {
                try {
                    const subject = N3.DataFactory.namedNode(entity["@id"]);
                    
                    // Add type triple
                    if (entity["@type"]) {
                        store.addQuad(
                            subject,
                            N3.DataFactory.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                            N3.DataFactory.namedNode(entity["@type"])
                        );
                    }
                    
                    // Add all other properties
                    Object.entries(entity).forEach(([predicate, value]) => {
                        // Skip @id and @type as they're handled separately
                        if (predicate === "@id" || predicate === "@type") return;
                        
                        const predicateNode = N3.DataFactory.namedNode(predicate);
                        
                        // Handle array values
                        if (Array.isArray(value)) {
                            value.forEach(v => {
                                try {
                                    if (typeof v === 'object' && v["@id"]) {
                                        // Reference to another entity
                                        store.addQuad(subject, predicateNode, N3.DataFactory.namedNode(v["@id"]));
                                    } else {
                                        // Literal value
                                        store.addQuad(subject, predicateNode, N3.DataFactory.literal(String(v)));
                                    }
                                } catch (innerError) {
                                    console.warn(`Error processing array value for ${predicate}:`, innerError);
                                }
                            });
                        } 
                        // Handle object values (references to other entities)
                        else if (typeof value === 'object' && value["@id"]) {
                            store.addQuad(subject, predicateNode, N3.DataFactory.namedNode(value["@id"]));
                        }
                        // Handle literal values
                        else {
                            store.addQuad(subject, predicateNode, N3.DataFactory.literal(String(value)));
                        }
                    });
                } catch (entityError) {
                    console.warn(`Error processing entity ${entity["@id"] || "unknown"}:`, entityError);
                    // Continue processing other entities
                }
            });
        } else {
            console.warn("No @graph found in JSON-LD data, trying to process as flat JSON-LD");
            
            // Try to process as flat JSON-LD (not in @graph format)
            // This is a fallback for simpler JSON-LD formats
            try {
                // Process context to get prefixes
                const context = jsonldData["@context"] || {};
                
                // Process each top-level entity that has an @id
                Object.entries(jsonldData).forEach(([key, value]) => {
                    if (key === "@context") return; // Skip context
                    
                    if (key === "@id") {
                        // This is a single entity at the root
                        const subject = N3.DataFactory.namedNode(value);
                        
                        // Add type if present
                        if (jsonldData["@type"]) {
                            store.addQuad(
                                subject,
                                N3.DataFactory.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                                N3.DataFactory.namedNode(jsonldData["@type"])
                            );
                        }
                        
                        // Add all other properties
                        Object.entries(jsonldData).forEach(([predicate, propValue]) => {
                            // Skip @id and @type as they're handled separately
                            if (predicate === "@id" || predicate === "@type" || predicate === "@context") return;
                            
                            const predicateNode = N3.DataFactory.namedNode(predicate);
                            
                            if (typeof propValue === 'object' && propValue["@id"]) {
                                // Reference to another entity
                                store.addQuad(subject, predicateNode, N3.DataFactory.namedNode(propValue["@id"]));
                            } else if (!Array.isArray(propValue) && typeof propValue !== 'object') {
                                // Literal value
                                store.addQuad(subject, predicateNode, N3.DataFactory.literal(String(propValue)));
                            }
                        });
                    }
                });
            } catch (flatError) {
                console.warn("Error processing flat JSON-LD:", flatError);
            }
        }
        
        console.log(`Added ${store.size} quads to N3 store`);
        
        if (store.size === 0) {
            throw new Error("No quads were added to the store. Check the JSON-LD format.");
        }
        
        // Debug: Print some sample quads
        console.log("Sample quads in store:");
        let count = 0;
        for (const quad of store) {
            if (count < 10) {
                console.log(`${quad.subject.value} ${quad.predicate.value} ${quad.object.value}`);
                count++;
            } else {
                break;
            }
        }
        
    } catch (error) {
        console.error('Error processing JSON-LD:', error);
        throw error;
    }
}

// Execute SPARQL query
async function executeQuery() {
    if (!store || store.size === 0) {
        showStatus('error', 'Please load a knowledge graph first');
        return;
    }

    const queryText = document.getElementById('queryEditor').value;
    if (!queryText.trim()) {
        showStatus('error', 'Please enter a SPARQL query');
        return;
    }

    try {
        showStatus('loading', 'Executing SPARQL query...');
        
        // Parse the SPARQL query using SPARQL.js
        const parsedQuery = sparqlParser.parse(queryText);
        console.log("Parsed query:", parsedQuery);
        
        // Execute the parsed SPARQL query
        const results = await executeSPARQLQuery(parsedQuery);
        displayResults(results);
        showStatus('success', `Query executed successfully! Found ${results.length} results.`);
    } catch (error) {
        console.error('Query execution error:', error);
        showStatus('error', 'Query execution error: ' + error.message);
    }
}

// Execute a SPARQL query against the N3 store
async function executeSPARQLQuery(parsedQuery) {
    try {
        console.log("Executing SPARQL query:", parsedQuery);
        console.log("Store has", store.size, "quads");
        
        // Currently only supporting SELECT queries
        if (parsedQuery.queryType !== 'SELECT') {
            throw new Error(`Query type '${parsedQuery.queryType}' not supported yet. Only SELECT queries are supported.`);
        }
        
        // Process the WHERE clause
        const results = processWhereClause(parsedQuery.where, parsedQuery.variables);
        
        // Apply any modifiers (LIMIT, OFFSET, ORDER BY)
        const finalResults = applyModifiers(results, parsedQuery);
        
        console.log("Query results:", finalResults);
        return finalResults;
        
    } catch (error) {
        console.error("SPARQL query execution error:", error);
        throw error;
    }
}

// Process the WHERE clause of a SPARQL query
function processWhereClause(whereClause, variables) {
    // Initialize results with an empty binding
    let bindings = [{}];
    
    // Process each element in the WHERE clause
    for (const element of whereClause) {
        switch (element.type) {
            case 'bgp':
                // Basic Graph Pattern
                bindings = processBGP(element.triples, bindings);
                break;
                
            case 'optional':
                // OPTIONAL pattern
                bindings = processOptional(element, bindings);
                break;
                
            case 'filter':
                // FILTER expression
                bindings = processFilter(element, bindings);
                break;
                
            case 'union':
                // UNION pattern
                bindings = processUnion(element, bindings);
                break;
                
            default:
                console.warn(`Unsupported pattern type: ${element.type}`);
        }
    }
    
    // Project the variables requested in the SELECT clause
    return projectVariables(bindings, variables);
}

// Process a Basic Graph Pattern
function processBGP(triples, bindings) {
    let results = bindings;
    
    // Process each triple pattern
    for (const triple of triples) {
        results = processTriplePattern(triple, results);
    }
    
    return results;
}

// Process a triple pattern against the N3 store with existing bindings
function processTriplePattern(pattern, bindings) {
    const newBindings = [];
    
    // For each existing binding
    bindings.forEach(binding => {
        // Create a quad pattern with bound variables replaced by their values
        const subject = bindTerm(pattern.subject, binding);
        const predicate = bindTerm(pattern.predicate, binding);
        const object = bindTerm(pattern.object, binding);
        
        // Query the store with the bound pattern
        const quads = store.getQuads(
            subject.termType === 'Variable' ? null : subject,
            predicate.termType === 'Variable' ? null : predicate,
            object.termType === 'Variable' ? null : object,
            null
        );
        
        // For each matching quad, create a new binding
        quads.forEach(quad => {
            const newBinding = { ...binding };
            
            // Bind variables to the values in the quad
            if (pattern.subject.termType === 'Variable') {
                newBinding[pattern.subject.value] = quad.subject;
            }
            if (pattern.predicate.termType === 'Variable') {
                newBinding[pattern.predicate.value] = quad.predicate;
            }
            if (pattern.object.termType === 'Variable') {
                newBinding[pattern.object.value] = quad.object;
            }
            
            newBindings.push(newBinding);
        });
    });
    
    return newBindings;
}

// Process an OPTIONAL pattern
function processOptional(optionalPattern, bindings) {
    // Make a copy of the current bindings
    const originalBindings = [...bindings];
    
    // Try to match the optional pattern
    const matchedBindings = processWhereClause(optionalPattern.patterns, bindings);
    
    // If no matches, return the original bindings
    if (matchedBindings.length === 0) {
        return originalBindings;
    }
    
    // Otherwise, return the matched bindings
    return matchedBindings;
}

// Process a FILTER expression
function processFilter(filterPattern, bindings) {
    // Filter the bindings based on the expression
    return bindings.filter(binding => {
        try {
            return evaluateExpression(filterPattern.expression, binding);
        } catch (error) {
            console.warn(`Error evaluating filter: ${error.message}`);
            return false;
        }
    });
}

// Process a UNION pattern
function processUnion(unionPattern, bindings) {
    // Process each pattern in the union
    const results = [];
    
    for (const pattern of unionPattern.patterns) {
        const patternResults = processWhereClause([pattern], bindings);
        results.push(...patternResults);
    }
    
    return results;
}

// Evaluate a SPARQL expression
function evaluateExpression(expression, binding) {
    switch (expression.type) {
        case 'operation':
            return evaluateOperation(expression, binding);
            
        case 'functionCall':
            return evaluateFunction(expression, binding);
            
        case 'bgp':
        case 'variable':
            return evaluateTerm(expression, binding);
            
        default:
            console.warn(`Unsupported expression type: ${expression.type}`);
            return false;
    }
}

// Evaluate a SPARQL operation
function evaluateOperation(operation, binding) {
    const operator = operation.operator;
    const args = operation.args.map(arg => evaluateExpression(arg, binding));
    
    switch (operator) {
        case '=':
            return args[0] === args[1];
        case '!=':
            return args[0] !== args[1];
        case '<':
            return args[0] < args[1];
        case '>':
            return args[0] > args[1];
        case '<=':
            return args[0] <= args[1];
        case '>=':
            return args[0] >= args[1];
        case '+':
            return args[0] + args[1];
        case '-':
            return args[0] - args[1];
        case '*':
            return args[0] * args[1];
        case '/':
            return args[0] / args[1];
        case '&&':
        case 'and':
            return args[0] && args[1];
        case '||':
        case 'or':
            return args[0] || args[1];
        case '!':
        case 'not':
            return !args[0];
        default:
            console.warn(`Unsupported operator: ${operator}`);
            return false;
    }
}

// Evaluate a SPARQL function call
function evaluateFunction(functionCall, binding) {
    const functionName = functionCall.function;
    const args = functionCall.args.map(arg => evaluateExpression(arg, binding));
    
    switch (functionName) {
        case 'str':
            return args[0].toString();
        case 'lang':
            return args[0].language || '';
        case 'datatype':
            return args[0].datatype || '';
        case 'bound':
            return args[0] !== undefined;
        case 'isIRI':
        case 'isURI':
            return args[0] && args[0].termType === 'NamedNode';
        case 'isBlank':
            return args[0] && args[0].termType === 'BlankNode';
        case 'isLiteral':
            return args[0] && args[0].termType === 'Literal';
        case 'regex':
            try {
                const pattern = new RegExp(args[1], args[2] || '');
                return pattern.test(args[0]);
            } catch (e) {
                console.warn(`Invalid regex: ${e.message}`);
                return false;
            }
        case 'strstarts':
            return args[0].startsWith(args[1]);
        case 'strends':
            return args[0].endsWith(args[1]);
        case 'contains':
            return args[0].includes(args[1]);
        default:
            console.warn(`Unsupported function: ${functionName}`);
            return false;
    }
}

// Evaluate a term in a SPARQL expression
function evaluateTerm(term, binding) {
    if (term.termType === 'Variable') {
        return binding[term.value] || null;
    }
    return term.value;
}

// Apply query modifiers (LIMIT, OFFSET, ORDER BY)
function applyModifiers(results, query) {
    let modifiedResults = [...results];
    
    // Apply ORDER BY
    if (query.order && query.order.length > 0) {
        modifiedResults.sort((a, b) => {
            for (const orderCondition of query.order) {
                const variable = orderCondition.expression.value;
                const aValue = a[variable] || '';
                const bValue = b[variable] || '';
                
                if (aValue < bValue) return orderCondition.descending ? 1 : -1;
                if (aValue > bValue) return orderCondition.descending ? -1 : 1;
            }
            return 0;
        });
    }
    
    // Apply OFFSET
    if (query.offset) {
        modifiedResults = modifiedResults.slice(query.offset);
    }
    
    // Apply LIMIT
    if (query.limit) {
        modifiedResults = modifiedResults.slice(0, query.limit);
    }
    
    return modifiedResults;
}

// Bind a term with values from the binding
function bindTerm(term, binding) {
    if (term.termType === 'Variable' && binding[term.value]) {
        return binding[term.value];
    }
    return term;
}

// Project the variables requested in the SELECT clause
function projectVariables(bindings, variables) {
    // If SELECT *, return all variables
    if (variables[0] && variables[0].value === '*') {
        return bindings.map(binding => {
            const result = {};
            Object.entries(binding).forEach(([key, value]) => {
                if (value) {
                    const shortKey = key.startsWith('?') ? key.substring(1) : key;
                    result[shortKey] = value.value;
                    result[shortKey + '_full'] = value.value;
                }
            });
            return result;
        });
    }
    
    // Otherwise, project only the requested variables
    return bindings.map(binding => {
        const result = {};
        variables.forEach(variable => {
            const varName = variable.value;
            const shortName = varName.startsWith('?') ? varName.substring(1) : varName;
            
            if (binding[varName]) {
                result[shortName] = binding[varName].value;
                
                // For entity URIs, also add a shortened version
                if (binding[varName].termType === 'NamedNode') {
                    const uri = binding[varName].value;
                    result[shortName] = uri.substring(uri.lastIndexOf('/') + 1);
                    result[shortName + '_full'] = uri;
                }
            } else {
                result[shortName] = null;
            }
        });
        return result;
    });
}

// Display entity details in a modal
function showEntityDetails(uri) {
    // Create a modal to display the entity details
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';
    
    // Create the modal content
    const modalContent = document.createElement('div');
    modalContent.style.backgroundColor = 'white';
    modalContent.style.padding = '20px';
    modalContent.style.borderRadius = '10px';
    modalContent.style.maxWidth = '80%';
    modalContent.style.maxHeight = '80%';
    modalContent.style.overflow = 'auto';
    
    // Add a close button
    const closeButton = document.createElement('button');
    closeButton.textContent = 'Close';
    closeButton.style.float = 'right';
    closeButton.style.marginBottom = '10px';
    closeButton.onclick = () => {
        document.body.removeChild(modal);
    };
    modalContent.appendChild(closeButton);
    
    // Add the entity URI
    const uriHeading = document.createElement('h3');
    uriHeading.textContent = 'Entity URI';
    modalContent.appendChild(uriHeading);
    
    const uriParagraph = document.createElement('p');
    uriParagraph.textContent = uri;
    modalContent.appendChild(uriParagraph);
    
    // Get entity properties from the store
    const entityNode = N3.DataFactory.namedNode(uri);
    const quads = store.getQuads(entityNode, null, null);
    
    if (quads.length > 0) {
        const propertiesHeading = document.createElement('h3');
        propertiesHeading.textContent = 'Properties';
        modalContent.appendChild(propertiesHeading);
        
        const propertiesList = document.createElement('dl');
        
        quads.forEach(quad => {
            const predicate = quad.predicate.value;
            const predicateName = predicate.substring(predicate.lastIndexOf('/') + 1);
            
            const dt = document.createElement('dt');
            dt.textContent = predicateName;
            dt.style.fontWeight = 'bold';
            dt.style.marginTop = '10px';
            propertiesList.appendChild(dt);
            
            const dd = document.createElement('dd');
            if (quad.object.termType === 'NamedNode') {
                const a = document.createElement('a');
                a.textContent = quad.object.value.substring(quad.object.value.lastIndexOf('/') + 1);
                a.href = '#';
                a.title = quad.object.value;
                a.onclick = (e) => {
                    e.preventDefault();
                    document.body.removeChild(modal);
                    showEntityDetails(quad.object.value);
                };
                dd.appendChild(a);
            } else {
                dd.textContent = quad.object.value;
            }
            propertiesList.appendChild(dd);
        });
        
        modalContent.appendChild(propertiesList);
    }
    
    // Add the modal content to the modal
    modal.appendChild(modalContent);
    
    // Add the modal to the document
    document.body.appendChild(modal);
}

// Display query results
function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    const contentDiv = document.getElementById('resultsContent');
    
    if (results.length === 0) {
        contentDiv.innerHTML = '<p>No results found.</p>';
    } else {
        // Create table
        const keys = Object.keys(results[0]).filter(k => !k.endsWith('_full')); // Filter out _full URIs
        let html = '<table><thead><tr>';
        keys.forEach(key => {
            html += `<th>${key}</th>`;
        });
        html += '</tr></thead><tbody>';
        
        results.forEach(result => {
            html += '<tr>';
            keys.forEach(key => {
                const value = result[key] || '';
                // If we have a full URI for this value, make it a link to show entity details
                if (result[`${key}_full`]) {
                    html += `<td><a href="#" onclick="event.preventDefault(); showEntityDetails('${result[`${key}_full`]}');" title="${result[`${key}_full`]}">${value}</a></td>`;
                } else {
                    html += `<td>${value}</td>`;
                }
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        
        contentDiv.innerHTML = html;
    }
    
    resultsDiv.style.display = 'block';
}

// Load predefined queries
function loadQuery(type) {
    const queries = {
        people: `PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?person ?name ?location ?role WHERE {
    ?person rdf:type myco:RegenerativePerson ;
            myco:name ?name .
    OPTIONAL { ?person myco:location ?location }
    OPTIONAL { ?person myco:currentRole ?role }
}`,
        projects: `PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tip ?name ?status WHERE {
    ?tip rdf:type myco:HyphalTip ;
         myco:name ?name .
    OPTIONAL { ?tip myco:activityStatus ?status }
}`,
        organizations: `PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?org ?name WHERE {
    ?org rdf:type myco:Organization ;
         myco:name ?name .
}`,
        collaborations: `PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?entity1 ?name1 ?entity2 ?name2 WHERE {
    ?entity1 myco:name ?name1 ;
             myco:collaborator ?entity2 .
    ?entity2 myco:name ?name2 .
}`,
        locations: `PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?entity ?name ?location WHERE {
    ?entity myco:name ?name ;
            myco:location ?location .
}`,
        network: `PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?entity ?name ?type WHERE {
    ?entity myco:name ?name ;
            rdf:type ?type .
    FILTER(STRSTARTS(STR(?type), STR(myco:)))
}`,
        advanced: `PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?entity ?name ?type ?related ?relatedName WHERE {
    ?entity myco:name ?name ;
            rdf:type ?type .
    {
        ?entity myco:collaborator ?related .
        ?related myco:name ?relatedName .
    } UNION {
        ?related myco:collaborator ?entity .
        ?related myco:name ?relatedName .
    }
    FILTER(?entity != ?related)
}
LIMIT 10`
    };
    
    document.getElementById('queryEditor').value = queries[type] || '';
}

// Format a SPARQL query
function formatQuery() {
    const queryText = document.getElementById('queryEditor').value;
    if (!queryText.trim()) {
        return;
    }
    
    try {
        // Parse the query
        const parsedQuery = sparqlParser.parse(queryText);
        
        // Generate a formatted query string
        const formattedQuery = sparqlGenerator.stringify(parsedQuery);
        
        // Update the query editor
        document.getElementById('queryEditor').value = formattedQuery;
    } catch (error) {
        console.error('Error formatting query:', error);
        showStatus('error', 'Error formatting query: ' + error.message);
    }
}

// Generate a SPARQL query string from a parsed query object
function generateSPARQLQuery(parsedQuery) {
    return sparqlGenerator.stringify(parsedQuery);
}

// Show status messages
function showStatus(type, message) {
    const statusDiv = document.getElementById('loadStatus');
    statusDiv.className = `status ${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    
    if (type === 'success') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 3000);
    }
}

// Clear results
function clearResults() {
    document.getElementById('results').style.display = 'none';
    document.getElementById('resultsContent').innerHTML = '';
}

// Initialize on page load
window.addEventListener('load', async () => {
    await initStore();
    
    // Automatically try to load the local knowledge graph
    const loaded = await loadLocalKnowledgeGraph();
    if (!loaded) {
        showStatus('error', 'Could not load mycomind_knowledge_graph.jsonld from repository');
    }
});
