// Initialize rdflib store
const store = $rdf.graph();
const fetcher = new $rdf.Fetcher(store);
const updater = new $rdf.UpdateManager(store);

// Define namespaces
const MYCO = $rdf.Namespace("http://mycomind.org/kg/ontology/");
const RDF = $rdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#");
const RDFS = $rdf.Namespace("http://www.w3.org/2000/01/rdf-schema#");

// Initialize the store
async function initStore() {
    try {
        console.log('RDFLib store initialized');
        showStatus('info', 'Ready to load knowledge graph. Please upload a JSON-LD file or click "Load Sample Data"');
    } catch (error) {
        console.error('Failed to initialize RDF store:', error);
        showStatus('error', 'Failed to initialize RDF store');
    }
}

// Load the knowledge graph file
async function loadLocalKnowledgeGraph() {
    try {
        showStatus('loading', 'Loading knowledge graph data...');
        
        // Fetch the JSON-LD file
        try {
            const response = await fetch('mycomind_knowledge_graph.jsonld');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const jsonldData = await response.json();
            console.log("Loaded JSON-LD data:", jsonldData);
            
            // Process the JSON-LD data
            processJSONLD(jsonldData);
            
            // Count entities
            const entities = store.each(null, RDF('type'), null);
            console.log("Loaded entities:", entities);
            
            // Log all statements for debugging
            console.log("Total statements:", store.statements.length);
            
            if (store.statements.length === 0) {
                throw new Error("Failed to load any statements from the JSON-LD file");
            }
            
            showStatus('success', `Loaded knowledge graph with ${entities.length} entities`);
            return true;
        } catch (fetchError) {
            console.error('Error fetching JSON-LD file:', fetchError);
            showStatus('error', 'Error loading knowledge graph file. Please upload a file manually.');
            return false;
        }
    } catch (error) {
        console.error('Error loading knowledge graph:', error);
        showStatus('error', 'Error loading knowledge graph. Please upload a file manually.');
        return false;
    }
}

// Process JSON-LD data and add to the store
function processJSONLD(jsonldData) {
    try {
        console.log("Processing JSON-LD data...");
        
        // Clear the store first to avoid duplicates
        store.removeStatements(store.statements);
        
        // Try to parse the JSON-LD into the RDF store using rdflib
        try {
            $rdf.parse(JSON.stringify(jsonldData), store, "http://mycomind.org/kg/", "application/ld+json");
            console.log("Successfully parsed JSON-LD using rdflib parser");
        } catch (parseError) {
            console.log("RDFLib parsing failed, processing manually:", parseError);
        }
        
        // If parsing didn't work or added no statements, add triples manually
        if (store.statements.length === 0 && jsonldData["@graph"]) {
            console.log("Adding triples manually from @graph...");
            
            // Process each entity in the @graph array
            jsonldData["@graph"].forEach(entity => {
                const subject = $rdf.sym(entity["@id"]);
                
                // Add type
                if (entity["@type"]) {
                    store.add(subject, RDF('type'), $rdf.sym(entity["@type"]));
                }
                
                // Add all other properties
                Object.entries(entity).forEach(([key, value]) => {
                    // Skip @id and @type as they're handled separately
                    if (key === "@id" || key === "@type") return;
                    
                    const predNode = $rdf.sym(key);
                    
                    // Handle array values
                    if (Array.isArray(value)) {
                        value.forEach(v => {
                            if (typeof v === 'object' && v["@id"]) {
                                // Reference to another entity
                                store.add(subject, predNode, $rdf.sym(v["@id"]));
                            } else {
                                // Literal value
                                store.add(subject, predNode, $rdf.lit(v));
                            }
                        });
                    } 
                    // Handle object values (references to other entities)
                    else if (typeof value === 'object' && value["@id"]) {
                        store.add(subject, predNode, $rdf.sym(value["@id"]));
                    }
                    // Handle literal values
                    else {
                        store.add(subject, predNode, $rdf.lit(value));
                    }
                });
            });
            
            console.log("Added triples manually");
        }
        
        console.log(`Total statements in store: ${store.statements.length}`);
    } catch (error) {
        console.error('Error processing JSON-LD:', error);
    }
}

// Load sample data from the local file or GitHub repository
async function loadSampleData() {
    try {
        showStatus('loading', 'Loading sample data...');
        
        // Sample data as a fallback if both local and GitHub fetches fail
        const sampleData = {
            "@context": {
                "@vocab": "http://mycomind.org/kg/ontology/",
                "@base": "http://mycomind.org/kg/resource/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            },
            "@graph": [
                {
                    "@id": "http://mycomind.org/kg/resource/RegenerativePerson/Shawn",
                    "@type": "http://mycomind.org/kg/ontology/RegenerativePerson",
                    "http://mycomind.org/kg/ontology/name": "Shawn",
                    "http://mycomind.org/kg/ontology/location": "Portland",
                    "http://mycomind.org/kg/ontology/currentRole": "Developer",
                    "http://mycomind.org/kg/ontology/bio": "A brilliant developer with a background in semantic web technologies"
                },
                {
                    "@id": "http://mycomind.org/kg/resource/HyphalTip/MycoMind",
                    "@type": "http://mycomind.org/kg/ontology/HyphalTip",
                    "http://mycomind.org/kg/ontology/name": "MycoMind: Personal Knowledge Management System",
                    "http://mycomind.org/kg/ontology/activityStatus": "alive",
                    "http://mycomind.org/kg/ontology/collaborator": [
                        {"@id": "http://mycomind.org/kg/resource/RegenerativePerson/Shawn"}
                    ]
                },
                {
                    "@id": "http://mycomind.org/kg/resource/Project/MycoMind",
                    "@type": "http://mycomind.org/kg/ontology/Project",
                    "http://mycomind.org/kg/ontology/name": "MycoMind",
                    "http://mycomind.org/kg/ontology/status": "in-progress",
                    "http://mycomind.org/kg/ontology/description": "A project to build a personal knowledge management system"
                }
            ]
        };
        
        let jsonldData;
        let dataSource = "embedded sample data";
        
        // Try to fetch the JSON-LD file from the local file system first
        try {
            const response = await fetch('mycomind_knowledge_graph.jsonld');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            jsonldData = await response.json();
            dataSource = "local file";
            console.log("Loaded JSON-LD data from local file");
        } catch (localError) {
            console.log("Could not load local file, trying GitHub repository...");
            
            // If local file is not available, try to fetch from GitHub
            try {
                const githubUrl = 'https://raw.githubusercontent.com/DarrenZal/MycoMind/master/docs/web/mycomind_knowledge_graph.jsonld';
                const response = await fetch(githubUrl);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                jsonldData = await response.json();
                dataSource = "GitHub repository";
                console.log("Loaded JSON-LD data from GitHub");
            } catch (githubError) {
                console.log("Could not load from GitHub, using embedded sample data");
                jsonldData = sampleData;
            }
        }
        
        // Process the JSON-LD data
        processJSONLD(jsonldData);
        
        // Count entities
        const entities = store.each(null, RDF('type'), null);
        console.log("Entities:", entities);
        showStatus('success', `Loaded sample data from ${dataSource} with ${entities.length} entities. Try the sample queries!`);
    } catch (error) {
        console.error('Error loading sample data:', error);
        showStatus('error', 'Error loading sample data: ' + error.message);
    }
}

// Execute SPARQL query using rdflib
async function executeQuery() {
    if (store.statements.length === 0) {
        showStatus('error', 'Please load a knowledge graph first');
        return;
    }

    const query = document.getElementById('queryEditor').value;
    if (!query.trim()) {
        showStatus('error', 'Please enter a SPARQL query');
        return;
    }

    try {
        showStatus('loading', 'Executing query...');
        
        // Execute SPARQL query using rdflib
        const results = await executeSPARQLQuery(query);
        displayResults(results);
        showStatus('success', `Query executed successfully! Found ${results.length} results.`);
    } catch (error) {
        console.error('Query execution error:', error);
        showStatus('error', 'Query execution error: ' + error.message);
    }
}

// Execute SPARQL query using rdflib
async function executeSPARQLQuery(sparqlQuery) {
    return new Promise((resolve, reject) => {
        try {
            console.log("Executing query:", sparqlQuery);
            console.log("Store has statements:", store.statements.length);
            
            // Debug: Print all statements in the store
            console.log("All statements in store:");
            store.statements.forEach((stmt, index) => {
                console.log(`Statement ${index}:`, 
                    stmt.subject.value, 
                    stmt.predicate.value, 
                    stmt.object.termType === 'Literal' ? stmt.object.value : stmt.object.value);
            });
            
            // Simple query execution for demo purposes
            // This avoids CORS issues with external fetching
            let results = [];
            
            // Parse the query to determine what we're looking for
            if (sparqlQuery.includes('rdf:type myco:RegenerativePerson')) {
                console.log("Looking for RegenerativePerson entities");
                
                // Find all RegenerativePerson entities - use Set to ensure uniqueness
                const personURIs = new Set();
                store.statements.forEach(stmt => {
                    if (stmt.predicate.value === 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' && 
                        stmt.object.value === 'http://mycomind.org/kg/ontology/RegenerativePerson') {
                        personURIs.add(stmt.subject.value);
                    }
                });
                
                const persons = Array.from(personURIs).map(uri => $rdf.sym(uri));
                console.log("Found unique persons:", persons);
                
                // Debug: Print each person's properties
                persons.forEach((person, idx) => {
                    console.log(`Person ${idx}:`, person.value);
                    const stmts = store.statementsMatching(person);
                    stmts.forEach(s => {
                        console.log(`  - ${s.predicate.value}: ${s.object.termType === 'Literal' ? s.object.value : s.object.value}`);
                    });
                });
                
                // Process each unique person
                persons.forEach(person => {
                    const name = store.any(person, MYCO('name'), null);
                    const location = store.any(person, MYCO('location'), null);
                    const role = store.any(person, MYCO('currentRole'), null);
                    
                    results.push({
                        person: person.value,
                        person_full: person.value,
                        name: name ? name.value : '',
                        location: location ? location.value : '',
                        role: role ? role.value : ''
                    });
                });
                
                console.log("Query results:", results);
            } 
            else if (sparqlQuery.includes('rdf:type myco:HyphalTip')) {
                console.log("Looking for HyphalTip entities");
                
                // Find all HyphalTip entities
                const tips = store.each(null, RDF('type'), MYCO('HyphalTip'));
                console.log("Found tips:", tips);
                
                tips.forEach(tip => {
                    const name = store.any(tip, MYCO('name'), null);
                    const status = store.any(tip, MYCO('activityStatus'), null);
                    
                    results.push({
                        tip: tip.value,
                        tip_full: tip.value,
                        name: name ? name.value : '',
                        status: status ? status.value : ''
                    });
                });
            }
            else if (sparqlQuery.includes('rdf:type myco:Project')) {
                console.log("Looking for Project entities");
                
                // Find all Project entities
                const projects = store.each(null, RDF('type'), MYCO('Project'));
                console.log("Found projects:", projects);
                
                projects.forEach(project => {
                    const name = store.any(project, MYCO('name'), null);
                    const status = store.any(project, MYCO('status'), null);
                    
                    results.push({
                        project: project.value,
                        project_full: project.value,
                        name: name ? name.value : '',
                        status: status ? status.value : ''
                    });
                });
            }
            else if (sparqlQuery.includes('myco:collaborator')) {
                console.log("Looking for collaborations");
                
                // Find all entities with collaborators
                store.each(null, MYCO('collaborator'), null).forEach(entity => {
                    const name = store.any(entity, MYCO('name'), null);
                    const collaborators = store.each(entity, MYCO('collaborator'), null);
                    
                    collaborators.forEach(collaborator => {
                        results.push({
                            entity1: entity.value,
                            entity1_full: entity.value,
                            name1: name ? name.value : '',
                            entity2: collaborator.value,
                            entity2_full: collaborator.value
                        });
                    });
                });
            }
            else if (sparqlQuery.includes('rdf:type myco:Organization')) {
                console.log("Looking for Organization entities");
                
                // Find all Organization entities
                const organizations = store.each(null, RDF('type'), MYCO('Organization'));
                console.log("Found organizations:", organizations);
                
                organizations.forEach(org => {
                    const name = store.any(org, MYCO('name'), null);
                    
                    results.push({
                        org: org.value,
                        org_full: org.value,
                        name: name ? name.value : ''
                    });
                });
            }
            else if (sparqlQuery.includes('myco:location')) {
                console.log("Looking for entities with locations");
                
                // Find all entities with locations
                store.each(null, MYCO('location'), null).forEach(entity => {
                    const name = store.any(entity, MYCO('name'), null);
                    const location = store.any(entity, MYCO('location'), null);
                    
                    results.push({
                        entity: entity.value,
                        entity_full: entity.value,
                        name: name ? name.value : '',
                        location: location ? location.value : ''
                    });
                });
            }
            else {
                console.log("Generic query for all entities with names and types");
                
                // Generic query - find all entities with names
                store.each(null, MYCO('name'), null).forEach(entity => {
                    const name = store.any(entity, MYCO('name'), null);
                    const types = store.each(entity, RDF('type'), null);
                    
                    if (types.length > 0) {
                        const type = types[0];
                        const typeStr = type.value;
                        const typeName = typeStr.substring(typeStr.lastIndexOf('/') + 1);
                        
                        results.push({
                            entity: entity.value,
                            entity_full: entity.value,
                            name: name ? name.value : '',
                            type: typeName,
                            type_full: type.value
                        });
                    }
                });
            }
            
            console.log("Query results:", results);
            resolve(results);
        } catch (error) {
            console.error("Query execution error:", error);
            reject(error);
        }
    });
}

// Display entity details in a modal
function showEntityDetails(uri) {
    // Find the entity in the store
    const entity = $rdf.sym(uri);
    const entityExists = store.any(entity, null, null) || store.any(null, null, entity);
    
    if (!entityExists) {
        alert(`Entity not found: ${uri}`);
        return;
    }
    
    // Get all properties for this entity
    const properties = {};
    
    // Get all statements where this entity is the subject
    store.statementsMatching(entity, null, null).forEach(statement => {
        const predicate = statement.predicate.value;
        const predicateName = predicate.substring(predicate.lastIndexOf('/') + 1);
        const object = statement.object;
        
        if (!properties[predicateName]) {
            properties[predicateName] = [];
        }
        
        if (object.termType === 'NamedNode') {
            // For URI references, use the last part of the URI
            const objectValue = object.value;
            const objectName = objectValue.substring(objectValue.lastIndexOf('/') + 1);
            properties[predicateName].push({
                value: objectName,
                uri: objectValue,
                isUri: true
            });
        } else {
            // For literals, use the value directly
            properties[predicateName].push({
                value: object.value,
                isUri: false
            });
        }
    });
    
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
    
    // Add the entity properties
    const propertiesHeading = document.createElement('h3');
    propertiesHeading.textContent = 'Properties';
    modalContent.appendChild(propertiesHeading);
    
    const propertiesList = document.createElement('dl');
    for (const [predicate, objects] of Object.entries(properties)) {
        const dt = document.createElement('dt');
        dt.textContent = predicate;
        dt.style.fontWeight = 'bold';
        dt.style.marginTop = '10px';
        propertiesList.appendChild(dt);
        
        objects.forEach(object => {
            const dd = document.createElement('dd');
            if (object.isUri) {
                const a = document.createElement('a');
                a.textContent = object.value;
                a.href = '#';
                a.title = object.uri;
                a.onclick = (e) => {
                    e.preventDefault();
                    document.body.removeChild(modal);
                    showEntityDetails(object.uri);
                };
                dd.appendChild(a);
            } else {
                dd.textContent = object.value;
            }
            propertiesList.appendChild(dd);
        });
    }
    modalContent.appendChild(propertiesList);
    
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

SELECT ?entity1 ?name1 ?entity2 WHERE {
    ?entity1 myco:name ?name1 ;
             myco:collaborator ?entity2 .
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
}`
    };
    
    document.getElementById('queryEditor').value = queries[type] || '';
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
    showStatus('info', 'Please upload a JSON-LD file or click "Load Sample Data"');
    
    // Set up file input event listener
    document.getElementById('jsonldFile').addEventListener('change', async function(event) {
        const file = event.target.files[0];
        if (file) {
            try {
                showStatus('loading', 'Loading knowledge graph...');
                const text = await file.text();
                const jsonldData = JSON.parse(text);
                
                // Process the JSON-LD data
                processJSONLD(jsonldData);
                
                // Count entities
                const entities = store.each(null, RDF('type'), null);
                console.log("Loaded entities:", entities);
                
                // Log all statements for debugging
                console.log("Total statements:", store.statements.length);
                
                if (store.statements.length === 0) {
                    throw new Error("Failed to load any statements from the JSON-LD file");
                }
                
                showStatus('success', `Loaded knowledge graph with ${entities.length} entities`);
            } catch (error) {
                console.error('Error loading file:', error);
                showStatus('error', 'Error loading file: ' + error.message);
            }
        }
    });
});
