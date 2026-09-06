/**
 * Mounts into #smashfire-pr-root (see class-admin-menu.php).
 * Phase 0: no real UI yet — just proves the build pipeline works.
 */
import { createRoot } from 'react-dom/client';

function App() {
	const root = document.getElementById( 'smashfire-pr-root' );
	const screen = root?.dataset.screen ?? 'unknown';
	return `Smashfire PR admin UI — screen: ${ screen } (Phase 2 fills this in)`;
}

const container = document.getElementById( 'smashfire-pr-root' );
if ( container ) {
	createRoot( container ).render( App() );
}
