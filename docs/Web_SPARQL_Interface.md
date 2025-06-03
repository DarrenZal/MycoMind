# Web SPARQL Interface

The MycoMind Web SPARQL Interface provides a browser-based way to query your knowledge graph using the SPARQL 1.1 query language. This interface uses SPARQL.js for full SPARQL 1.1 support, allowing you to run complex queries directly in your browser without requiring an external SPARQL endpoint.

## Features

- **Full SPARQL 1.1 Support**: Execute standard-compliant SPARQL 1.1 queries
- **In-browser Processing**: No need for external SPARQL endpoints
- **Interactive Entity Exploration**: Click on entity links to explore their properties
- **Query Formatting**: Format your queries for better readability
- **Sample Queries**: Pre-defined queries to help you get started
- **JSON-LD Integration**: Automatically loads your knowledge graph from JSON-LD files

## Getting Started

1. Open `docs/web/index.html` in your web browser
2. The interface will automatically load the knowledge graph from `docs/web/mycomind_knowledge_graph.jsonld`
3. Select a sample query or write your own SPARQL query
4. Click "Execute Query" to run the query and see the results

## Sample Queries

The interface includes several sample queries to help you get started:

### Find People

```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?person ?name ?location ?role WHERE {
    ?person rdf:type myco:RegenerativePerson ;
            myco:name ?name .
    OPTIONAL { ?person myco:location ?location }
    OPTIONAL { ?person myco:currentRole ?role }
}
```

### Find Projects

```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tip ?name ?status WHERE {
    ?tip rdf:type myco:HyphalTip ;
         myco:name ?name .
    OPTIONAL { ?tip myco:activityStatus ?status }
}
```

### Find Collaborations

```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?entity1 ?name1 ?entity2 ?name2 WHERE {
    ?entity1 myco:name ?name1 ;
             myco:collaborator ?entity2 .
    ?entity2 myco:name ?name2 .
}
```

### Advanced SPARQL 1.1 Features

```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>
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
LIMIT 10
```

## SPARQL.js Integration

The interface uses SPARQL.js to parse and execute SPARQL queries. SPARQL.js is a JavaScript library that provides a parser and generator for SPARQL 1.1 queries. It supports:

- Basic Graph Patterns
- OPTIONAL clauses
- UNION clauses
- FILTER expressions
- Property Paths
- Aggregates (COUNT, SUM, AVG, etc.)
- GROUP BY, ORDER BY, LIMIT, OFFSET
- BIND expressions
- VALUES clauses
- Subqueries
- SPARQL* (RDF-star) support

## Technical Details

### Architecture

The Web SPARQL Interface consists of:

1. **HTML/CSS Interface**: The user interface for entering queries and displaying results
2. **N3.js**: A JavaScript library for parsing and manipulating RDF data
3. **SPARQL.js**: A JavaScript library for parsing and executing SPARQL queries
4. **Custom JavaScript**: Code that ties everything together and implements the query execution logic

### Query Execution Flow

1. User enters a SPARQL query in the editor
2. SPARQL.js parses the query into a JSON representation
3. The custom JavaScript code processes the query against the in-memory RDF store
4. Results are formatted and displayed in the interface

### Customization

You can customize the interface by:

- Modifying the CSS styles in `docs/web/index.html`
- Adding new sample queries to the `loadQuery` function in `docs/web/mycomind-query.js`
- Extending the query execution logic in `docs/web/mycomind-query.js`

## Comparison with Other Query Interfaces

| Feature | Web SPARQL Interface | Neo4j Browser | Apache Jena Fuseki |
|---------|---------------------|---------------|-------------------|
| **Query Language** | SPARQL 1.1 | Cypher | SPARQL 1.1 |
| **Setup Complexity** | Low (browser-only) | Medium | Medium |
| **Visualization** | Basic tables | Interactive graph | Basic tables |
| **Performance** | Good for small-medium graphs | Excellent | Excellent |
| **Deployment** | Static files | Requires Neo4j server | Requires Fuseki server |
| **Advanced Features** | SPARQL 1.1 standard | Graph algorithms, procedures | Full SPARQL compliance |

## Troubleshooting

### Common Issues

1. **Knowledge graph not loading**
   - Check that `mycomind_knowledge_graph.jsonld` exists in the `docs/web` directory
   - Verify that the JSON-LD file is valid

2. **Query execution errors**
   - Check your SPARQL syntax
   - Use the "Format Query" button to help identify syntax issues
   - Verify that the prefixes you're using are defined

3. **No results returned**
   - Verify that your query matches the structure of your knowledge graph
   - Try a simpler query to confirm that the knowledge graph is loaded correctly

### Browser Compatibility

The Web SPARQL Interface works best with modern browsers:

- Chrome 60+
- Firefox 60+
- Safari 12+
- Edge 79+

## Future Enhancements

Planned enhancements for the Web SPARQL Interface include:

- Graph visualization of query results
- Query history and saving
- More advanced SPARQL 1.1 features (SERVICE, GRAPH, etc.)
- Performance optimizations for larger knowledge graphs
- Integration with external SPARQL endpoints
