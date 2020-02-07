const path = require('path');
const express = require('express');
const cors = require('cors');
const dps = require('dbpedia-sparql-client').default;

const app = express();

const allowedOrigins = ['http://127.0.0.1', 'http://localhost'];
app.use(
	cors({
		origin: function(origin, callback) {
			if (!origin) return callback(null, true);
			if (
				allowedOrigins.every(function(allowedOrigin) {
					return !origin.startsWith(allowedOrigin);
				})
			) {
				return callback(
					new Error(
						'The CORS policy for this site does not allow access from the specified Origin.'
					),
					false
				);
			}

			return callback(null, true);
		}
	})
);

app.use(express.static(path.join(__dirname, '../client')));

app.get('/', function(request, response) {
	response.sendFile(path.join(__dirname, '../client/'));
});

app.get('/test', function(request, response) {
	const q = ` SELECT DISTINCT ?y WHERE 
		{
			?x <www.w3.org/2000/01/rdf-schema#isDefinedBy> "http://dbpedia.org/ontology/"
		}
	`;
	const x = dps
		.client()
		.query()
		.query(q)
		.timeout(30)
		.asJson()
		.then((r) => {
			const { bindings } = r.results;
			console.log(bindings.map((x) => x.Monarch.value));
			// console.log(r);
			// response.send(r);
		})
		.catch((e) => {
			console.log('error', e);
		});
});

app.listen(3000, function() {
	console.log('Example app listening on port 3000!');
});
