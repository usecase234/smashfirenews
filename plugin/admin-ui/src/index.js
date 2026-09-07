/**
 * Mounts into #smashfire-pr-root (see class-admin-menu.php).
 *
 * Phase 3: Incoming and Drafts pull live from the Hub through the plugin's
 * REST proxy (class-rest-routes.php) — there is no local mirror to read
 * from instead, so every render re-fetches. Published/Senders/Settings stay
 * Phase 0 placeholders; nothing in Phase 3 needs them yet.
 */
import { createRoot } from 'react-dom/client';
import { useEffect, useState } from 'react';

const { restUrl, nonce } = window.smashfirePR ?? {};

async function callApi( path, method = 'GET' ) {
	const response = await fetch( restUrl + path, {
		method,
		headers: { 'X-WP-Nonce': nonce },
	} );
	const body = await response.json();
	if ( ! response.ok ) {
		throw new Error( body?.error ?? `Request failed (${ response.status })` );
	}
	return body;
}

function IncomingQueue() {
	const [ items, setItems ] = useState( null );
	const [ error, setError ] = useState( null );
	const [ busyId, setBusyId ] = useState( null );

	const load = () => {
		callApi( 'queue' ).then( setItems ).catch( ( e ) => setError( e.message ) );
	};

	useEffect( load, [] );

	const generateDraft = ( id ) => {
		setBusyId( id );
		setError( null );
		callApi( `submissions/${ id }/generate-draft`, 'POST' )
			.then( load )
			.catch( ( e ) => setError( e.message ) )
			.finally( () => setBusyId( null ) );
	};

	if ( error ) return <p style={ { color: 'red' } }>{ error }</p>;
	if ( items === null ) return <p>Loading…</p>;
	if ( items.length === 0 ) return <p>Nothing waiting.</p>;

	return (
		<table className="widefat">
			<thead>
				<tr>
					<th>Headline</th>
					<th>Sender</th>
					<th>Received</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{ items.map( ( item ) => (
					<tr key={ item.id }>
						<td>{ item.headline }</td>
						<td>{ item.sender_name }{ item.sender_company ? ` (${ item.sender_company })` : '' }</td>
						<td>{ new Date( item.created_at ).toLocaleString() }</td>
						<td>
							<button
								className="button button-primary"
								disabled={ busyId === item.id }
								onClick={ () => generateDraft( item.id ) }
							>
								{ busyId === item.id ? 'Generating…' : 'Generate Draft' }
							</button>
						</td>
					</tr>
				) ) }
			</tbody>
		</table>
	);
}

function DraftsQueue() {
	const [ items, setItems ] = useState( null );
	const [ error, setError ] = useState( null );
	const [ busyId, setBusyId ] = useState( null );

	const load = () => {
		callApi( 'drafts' ).then( setItems ).catch( ( e ) => setError( e.message ) );
	};

	useEffect( load, [] );

	const publish = ( id ) => {
		setBusyId( id );
		setError( null );
		callApi( `submissions/${ id }/publish`, 'POST' )
			.then( ( result ) => {
				load();
				if ( result.live_url ) {
					window.alert( `Published: ${ result.live_url }` );
				}
			} )
			.catch( ( e ) => setError( e.message ) )
			.finally( () => setBusyId( null ) );
	};

	if ( error ) return <p style={ { color: 'red' } }>{ error }</p>;
	if ( items === null ) return <p>Loading…</p>;
	if ( items.length === 0 ) return <p>No finished drafts yet.</p>;

	return (
		<table className="widefat">
			<thead>
				<tr>
					<th>Headline</th>
					<th>Sender</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{ items.map( ( item ) => (
					<tr key={ item.id }>
						<td>{ item.headline }</td>
						<td>{ item.sender_name }{ item.sender_company ? ` (${ item.sender_company })` : '' }</td>
						<td>
							<button
								className="button button-primary"
								disabled={ busyId === item.id }
								onClick={ () => publish( item.id ) }
							>
								{ busyId === item.id ? 'Publishing…' : 'Publish Now' }
							</button>
						</td>
					</tr>
				) ) }
			</tbody>
		</table>
	);
}

function App( { screen } ) {
	if ( ! restUrl ) {
		return <p>Smashfire PR admin script loaded without REST config — reload the page.</p>;
	}
	if ( screen === 'incoming' ) return <IncomingQueue />;
	if ( screen === 'drafts' ) return <DraftsQueue />;
	return <p>Smashfire PR admin UI — screen: { screen } (not wired up yet)</p>;
}

const container = document.getElementById( 'smashfire-pr-root' );
if ( container ) {
	const screen = container.dataset.screen ?? 'unknown';
	createRoot( container ).render( <App screen={ screen } /> );
}
