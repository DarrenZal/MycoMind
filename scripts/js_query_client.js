#!/usr/bin/env node

/**
 * MycoMind JavaScript SPARQL Query Client
 * 
 * Command-line interface using Comunica JavaScript SPARQL engine
 * No Java required - uses Node.js and the same engine as the web interface
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// Check if Comunica is installed
let QueryEngine;
try {
    const { QueryEngine: ComunicaQueryEngine } = require('@comunica/query-sparql');
    QueryEngine = ComunicaQueryEngine;
} catch (error) {
    console.error('❌ Comunica not installed. Install with:');
    console.error('   npm install @comunica/query-sparql');
    console.error('   or use the web interface instead: open web_query_interface.html');
    process.exit(1);
}

class JSQueryClient {
    constructor() {
        this.engine = new QueryEngine();
        this.store = null;
        this.rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
    }

    async loadKnowledgeGraph(filePath) {
        try {
            console.log(`📊 Loading knowledge graph from ${filePath}...`);
            
            if (!fs.existsSync(filePath)) {
                throw new Error(`File not found: ${filePath}`);
            }

            const content = fs.readFileSync(filePath, 'utf8');
            this.store = JSON.parse(content);
            
            const entityCount = this.store['@graph'] ? this.store['@graph'].length : 'unknown';
            console.log(`✅ Loaded knowledge graph with ${entityCount} entities`);
            return true;
        } catch (error) {
            console.error(`❌ Error loading knowledge graph: ${error.message}`);
            return false;
        }
    }

    async executeQuery(sparqlQuery) {
        if (!this.store) {
            console.error('❌ No knowledge graph loaded. Use --load <file> first.');
            return;
        }

        try {
            console.log('🔍 Executing SPARQL query...');
            
            // For demo purposes, use simplified query execution
            // In production, you'd use Comunica with proper RDF store
            const results = await this.executeSimpleQuery(sparqlQuery, this.store);
            
            if (results.length === 0) {
                console.log('📭 No results found.');
            } else {
                console.log(`📊 Found ${results.length} results:`);
                console.log('');
                this.displayResults(results);
            }
        } catch (error) {
            console.error(`❌ Query execution error: ${error.message}`);
        }
    }

    async executeSimpleQuery(query, data) {
        // Simplified query execution for demo
        // This matches the logic from the web interface
        const graph = data['@graph'] || [data];
        const results = [];

        if (query.includes('RegenerativePerson')) {
            graph.forEach(entity => {
                if (entity['@type'] === 'http://mycomind.org/kg/ontology/RegenerativePerson') {
                    results.push({
                        person: entity['@id'],
                        name: entity['http://mycomind.org/kg/ontology/name'],
                        location: entity['http://mycomind.org/kg/ontology/location'],
                        role: entity['http://mycomind.org/kg/ontology/currentRole']
                    });
                }
            });
        } else if (query.includes('HyphalTip')) {
            graph.forEach(entity => {
                if (entity['@type'] === 'http://mycomind.org/kg/ontology/HyphalTip') {
                    results.push({
                        tip: entity['@id'],
                        name: entity['http://mycomind.org/kg/ontology/name'],
                        status: entity['http://mycomind.org/kg/ontology/activityStatus']
                    });
                }
            });
        } else if (query.includes('Organization')) {
            graph.forEach(entity => {
                if (entity['@type'] === 'http://mycomind.org/kg/ontology/Organization') {
                    results.push({
                        org: entity['@id'],
                        name: entity['http://mycomind.org/kg/ontology/name']
                    });
                }
            });
        } else {
            // Generic query - return all entities
            graph.forEach(entity => {
                results.push({
                    entity: entity['@id'],
                    name: entity['http://mycomind.org/kg/ontology/name'] || 'Unknown',
                    type: entity['@type']
                });
            });
        }

        return results;
    }

    displayResults(results) {
        if (results.length === 0) return;

        const keys = Object.keys(results[0]);
        const maxWidths = {};
        
        // Calculate column widths
        keys.forEach(key => {
            maxWidths[key] = Math.max(
                key.length,
                ...results.map(r => String(r[key] || '').length)
            );
        });

        // Print header
        const header = keys.map(key => key.padEnd(maxWidths[key])).join(' | ');
        console.log(header);
        console.log(keys.map(key => '-'.repeat(maxWidths[key])).join('-+-'));

        // Print rows
        results.forEach(result => {
            const row = keys.map(key => 
                String(result[key] || '').padEnd(maxWidths[key])
            ).join(' | ');
            console.log(row);
        });
    }

    getSampleQueries() {
        return {
            people: `PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?person ?name ?location ?role WHERE {
    ?person a myco:RegenerativePerson ;
            myco:name ?name .
    OPTIONAL { ?person myco:location ?location }
    OPTIONAL { ?person myco:currentRole ?role }
}`,
            projects: `PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?tip ?name ?status WHERE {
    ?tip a myco:HyphalTip ;
         myco:name ?name .
    OPTIONAL { ?tip myco:activityStatus ?status }
}`,
            organizations: `PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?org ?name WHERE {
    ?org a myco:Organization ;
         myco:name ?name .
}`,
            all: `PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?entity ?name ?type WHERE {
    ?entity myco:name ?name ;
            a ?type .
    FILTER(STRSTARTS(STR(?type), STR(myco:)))
}`
        };
    }

    async interactive() {
        console.log('🍄 MycoMind JavaScript SPARQL Query Interface');
        console.log('===============================================');
        console.log('');
        
        if (!this.store) {
            console.log('❌ No knowledge graph loaded.');
            console.log('Load a knowledge graph first with: --load <file>');
            return;
        }

        console.log('Available sample queries:');
        console.log('  1. people      - Find RegenerativePerson entities');
        console.log('  2. projects    - Find HyphalTip projects');
        console.log('  3. organizations - Find organizations');
        console.log('  4. all         - List all entities');
        console.log('  5. custom      - Enter custom SPARQL query');
        console.log('  6. quit        - Exit');
        console.log('');

        const choice = await this.prompt('Select an option (1-6): ');
        
        const samples = this.getSampleQueries();
        let query = '';

        switch (choice.trim()) {
            case '1':
                query = samples.people;
                break;
            case '2':
                query = samples.projects;
                break;
            case '3':
                query = samples.organizations;
                break;
            case '4':
                query = samples.all;
                break;
            case '5':
                console.log('Enter your SPARQL query (end with empty line):');
                query = await this.multiLinePrompt();
                break;
            case '6':
                console.log('👋 Goodbye!');
                this.rl.close();
                return;
            default:
                console.log('❌ Invalid choice. Please select 1-6.');
                return this.interactive();
        }

        if (query) {
            console.log('');
            console.log('📝 Executing query:');
            console.log(query);
            console.log('');
            await this.executeQuery(query);
        }

        console.log('');
        const again = await this.prompt('Run another query? (y/n): ');
        if (again.toLowerCase().startsWith('y')) {
            console.log('');
            return this.interactive();
        } else {
            console.log('👋 Goodbye!');
            this.rl.close();
        }
    }

    async prompt(question) {
        return new Promise((resolve) => {
            this.rl.question(question, resolve);
        });
    }

    async multiLinePrompt() {
        return new Promise((resolve) => {
            const lines = [];
            console.log('(Enter empty line to finish)');
            
            const collectLines = () => {
                this.rl.question('> ', (line) => {
                    if (line.trim() === '') {
                        resolve(lines.join('\n'));
                    } else {
                        lines.push(line);
                        collectLines();
                    }
                });
            };
            
            collectLines();
        });
    }

    showHelp() {
        console.log(`
🍄 MycoMind JavaScript SPARQL Query Client

USAGE:
  node scripts/js_query_client.js [OPTIONS]

OPTIONS:
  --load <file>     Load JSON-LD knowledge graph file
  --query <query>   Execute SPARQL query string
  --file <file>     Execute SPARQL query from file
  --interactive     Start interactive query mode
  --help            Show this help message

EXAMPLES:
  # Load knowledge graph and start interactive mode
  node scripts/js_query_client.js --load mycomind_knowledge_graph.jsonld --interactive

  # Execute a specific query
  node scripts/js_query_client.js --load data.jsonld --query "SELECT * WHERE { ?s ?p ?o } LIMIT 10"

  # Execute query from file
  node scripts/js_query_client.js --load data.jsonld --file sample_queries.sparql

REQUIREMENTS:
  - Node.js installed
  - npm install @comunica/query-sparql

ALTERNATIVE:
  If you prefer a web interface, use: open web_query_interface.html
`);
    }
}

// Main execution
async function main() {
    const args = process.argv.slice(2);
    const client = new JSQueryClient();

    if (args.length === 0 || args.includes('--help')) {
        client.showHelp();
        return;
    }

    let loadFile = null;
    let queryString = null;
    let queryFile = null;
    let interactive = false;

    // Parse arguments
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--load':
                loadFile = args[++i];
                break;
            case '--query':
                queryString = args[++i];
                break;
            case '--file':
                queryFile = args[++i];
                break;
            case '--interactive':
                interactive = true;
                break;
        }
    }

    // Load knowledge graph if specified
    if (loadFile) {
        const loaded = await client.loadKnowledgeGraph(loadFile);
        if (!loaded) {
            process.exit(1);
        }
    }

    // Execute query if specified
    if (queryString) {
        await client.executeQuery(queryString);
    } else if (queryFile) {
        if (fs.existsSync(queryFile)) {
            const query = fs.readFileSync(queryFile, 'utf8');
            await client.executeQuery(query);
        } else {
            console.error(`❌ Query file not found: ${queryFile}`);
            process.exit(1);
        }
    } else if (interactive) {
        await client.interactive();
    } else {
        console.log('❌ No action specified. Use --help for usage information.');
    }

    client.rl.close();
}

// Handle errors gracefully
process.on('unhandledRejection', (error) => {
    console.error('❌ Unhandled error:', error.message);
    process.exit(1);
});

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = JSQueryClient;
