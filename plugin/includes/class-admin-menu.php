<?php
/**
 * Registers the five admin screens named in the source plan:
 * Incoming, Drafts, Published, Senders, Settings. Each renders a React root
 * (see admin-ui/src/index.js); Phase 3 wires up Incoming and Drafts against
 * the Hub, Published/Senders/Settings remain placeholders.
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
		add_action( 'admin_enqueue_scripts', array( __CLASS__, 'enqueue_admin_ui' ) );
	}

	/**
	 * Loads the built admin-ui bundle only on this plugin's own screens,
	 * and hands it the REST root + nonce it needs to call class-rest-routes.php
	 * (Incoming/Drafts pull live from the Hub — there is no local mirror to
	 * read from instead).
	 */
	public static function enqueue_admin_ui( string $hook_suffix ): void {
		if ( ! str_contains( $hook_suffix, 'smashfire-pr' ) ) {
			return;
		}

		$asset_file = SMASHFIRE_PR_DIR . 'admin-ui/build/index.asset.php';
		if ( ! file_exists( $asset_file ) ) {
			return; // `npm run build` hasn't been run in admin-ui/ yet.
		}
		$asset = require $asset_file;

		wp_enqueue_script(
			'smashfire-pr-admin-ui',
			SMASHFIRE_PR_URL . 'admin-ui/build/index.js',
			$asset['dependencies'],
			$asset['version'],
			true
		);

		wp_localize_script(
			'smashfire-pr-admin-ui',
			'smashfirePR',
			array(
				'restUrl' => esc_url_raw( rest_url( Smashfire_PR_Rest_Routes::REST_NAMESPACE . '/' ) ),
				'nonce'   => wp_create_nonce( 'wp_rest' ),
			)
		);
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
		echo '<div id="smashfire-pr-root" data-screen="' . esc_attr( strtolower( $label ) ) . '"></div></div>';
	}
}
