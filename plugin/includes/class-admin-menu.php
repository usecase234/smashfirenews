<?php
/**
 * Registers the five admin screens named in the source plan:
 * Incoming, Drafts, Published, Senders, Settings. Each renders an empty
 * React root for now — Phase 2 fills these in.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

class Smashfire_PR_Admin_Menu {

	private const SCREENS = array(
		'incoming'  => 'Incoming',
		'drafts'    => 'Drafts',
		'published' => 'Published',
		'senders'   => 'Senders',
		'settings'  => 'Settings',
	);

	public static function register(): void {
		add_action( 'admin_menu', array( __CLASS__, 'add_menu_pages' ) );
	}

	public static function add_menu_pages(): void {
		add_menu_page(
			'Smashfire PR',
			'Smashfire PR',
			'edit_posts',
			'smashfire-pr-incoming',
			array( __CLASS__, 'render_screen_incoming' ),
			'dashicons-megaphone'
		);

		foreach ( self::SCREENS as $slug => $label ) {
			add_submenu_page(
				'smashfire-pr-incoming',
				"Smashfire PR — {$label}",
				$label,
				'edit_posts',
				"smashfire-pr-{$slug}",
				fn() => self::render_placeholder( $label )
			);
		}
	}

	public static function render_screen_incoming(): void {
		self::render_placeholder( 'Incoming' );
	}

	private static function render_placeholder( string $label ): void {
		echo '<div class="wrap"><h1>Smashfire PR — ' . esc_html( $label ) . '</h1>';
		echo '<div id="smashfire-pr-root" data-screen="' . esc_attr( strtolower( $label ) ) . '"></div>';
		echo '<p><em>React app mounts here in Phase 2.</em></p></div>';
	}
}
